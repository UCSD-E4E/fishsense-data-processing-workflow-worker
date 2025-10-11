import numpy as np


def image_coordinate_to_projected_point(
    image_point: np.ndarray, inverted_camera_matrix: np.ndarray
) -> np.ndarray:
    assert isinstance(image_point, np.ndarray)
    assert isinstance(inverted_camera_matrix, np.ndarray)

    homogenous_point_image_space = np.zeros(3, dtype=float)
    homogenous_point_image_space[:2] = image_point
    homogenous_point_image_space[2] = 1

    # define laser ray assuming pinhole camera
    return inverted_camera_matrix @ homogenous_point_image_space


def image_coordinate_to_projected_point_vec(
    image_points: np.ndarray, pixel_pitch_mm: float, focal_length_mm: float
) -> np.ndarray:
    assert isinstance(image_points, np.ndarray)
    I_project = image_points * pixel_pitch_mm / 1e3
    I = np.zeros((I_project.shape[0], I_project.shape[1] + 1))
    I[..., :-1] = I_project
    I[..., -1] = -focal_length_mm * 1e-3
    return I


def compute_world_point_from_depth(
    image_coordinate: np.ndarray, depth: float, inverted_camera_matrix: np.ndarray
) -> np.ndarray:
    # Assumes the depth is known, calculates world point based on image point
    projected_point = image_coordinate_to_projected_point(
        image_point=image_coordinate, inverted_camera_matrix=inverted_camera_matrix
    )
    v = -projected_point / np.linalg.norm(projected_point)
    return v * depth / v[2]


def compute_world_points_from_depths(
    camera_params: tuple, image_coordinates: np.ndarray, depths: np.ndarray
) -> np.ndarray:
    # Assumes the depth is known, calculates world point based on image point
    projected_point = image_coordinate_to_projected_point_vec(
        image_points=image_coordinates,
        pixel_pitch_mm=camera_params[3],
        focal_length_mm=camera_params[0],
    )
    v = -projected_point / (np.linalg.norm(projected_point, axis=1)[..., np.newaxis])
    return v * depths[:, np.newaxis] / v[:, 2, np.newaxis]


def compute_world_point(
    laser_origin: np.ndarray,
    laser_axis: np.ndarray,
    inverted_camera_matrix: np.ndarray,
    image_coordinate: np.ndarray,
) -> np.ndarray:
    projected_point = image_coordinate_to_projected_point(
        image_point=image_coordinate, inverted_camera_matrix=inverted_camera_matrix
    )
    final_laser_axis = -1 * projected_point / np.linalg.norm(projected_point)

    # point_constant = (-1 * laser_axis[2] * laser_origin[0]) / \
    #     (laser_axis[0] * final_laser_axis[2] - laser_axis[2] * final_laser_axis[0])

    # Least squares
    point_constant = (
        (final_laser_axis.T @ laser_origin)
        - ((laser_axis.T @ laser_origin) * (laser_axis.T @ final_laser_axis))
    ) / (1 - (laser_axis.T @ final_laser_axis) ** 2)

    world_point = point_constant * final_laser_axis
    return world_point


def compute_world_points(
    laser_origin: np.ndarray,
    laser_axis: np.ndarray,
    inverted_camera_matrix: np.ndarray,
    image_coordinates: np.ndarray,
) -> np.ndarray:
    projected_points = image_coordinate_to_projected_point_vec(
        image_points=image_coordinates, inverted_camera_matrix=inverted_camera_matrix
    )
    final_laser_axes = (
        -1
        * projected_points
        / np.linalg.norm(projected_points, axis=1)[..., np.newaxis]
    )
    point_constants = (
        (final_laser_axes @ laser_origin)
        - ((laser_axis.T @ laser_origin) * (laser_axis @ final_laser_axes.T))
    ) / (1 - (laser_axis.T @ final_laser_axes.T) ** 2)
    world_points = point_constants[..., np.newaxis] * final_laser_axes
    return world_points


def atanasov_calibration_method(ps: np.ndarray):
    """
    Nikolay's method for laser calibration.
    Inputs:
     - ps: the laser points
    Output: the 5-vector of the laser parameters, with the first 3 being the orientation,
            and the final two being the x and y coordinates of the laser origin
    """
    avg_alpha = np.zeros((3,))
    params = np.zeros((5,))
    for i in range(ps.shape[0]):
        for j in range(ps.shape[0]):
            if i != j:
                v = ps[i] - ps[j]
                if v[2] < 0:
                    v = -v
                avg_alpha += v

    avg_alpha /= np.linalg.norm(avg_alpha)
    if avg_alpha[2] < 0:
        avg_alpha = -avg_alpha

    centroid = np.mean(ps, axis=0)
    scale_factor = centroid[2] / avg_alpha[2]
    params[0:3] = avg_alpha
    params[3:5] = centroid[0:2] - scale_factor * avg_alpha[0:2]
    return params


def get_jacobian(ps: np.ndarray, state: np.ndarray) -> np.ndarray:
    n = ps.shape[0]
    jacobian = np.zeros((n * 3, 5))
    alpha = state[:3]
    l = np.array([state[3], state[4], 0])
    for i in range(n):
        p = ps[i]
        jacobian[3 * i : 3 * i + 3, :3] = np.eye(3) * np.linalg.norm(p - l)
        jacobian[3 * i : 3 * i + 3, 3:5] = (
            alpha[:, np.newaxis] @ (p - l)[np.newaxis, :2]
        ) / np.linalg.norm(p - l)
        jacobian[[3 * i, 3 * i + 1], [3, 4]] *= -1
        jacobian[[3 * i, 3 * i + 1], [3, 4]] += 1
    return jacobian


def get_residual(points: np.ndarray, state: np.ndarray) -> float:
    laser_pos = np.array([state[3], state[4], 0])
    laser_angle = state[:3]
    est_points = (
        np.linalg.norm(points - laser_pos, axis=1)[:, np.newaxis] * laser_angle
        + laser_pos
    )
    return points - est_points


def gauss_newton_estimate_state(
    ps: np.ndarray, init_state: np.ndarray, num_iterations: int = 10
) -> np.ndarray:
    state = init_state
    residual_norm_squared = []
    for _ in range(num_iterations):
        J = get_jacobian(ps, state)
        rs = get_residual(ps, state).flatten()
        residual_norm_squared.append(np.dot(rs, rs))
        temp_state = state + np.linalg.pinv(J) @ rs
        state = temp_state
    return state, residual_norm_squared


def test_run():
    sensor_size_px = np.array([4000, 3000])
    pixel_pitch_mm = 0.0015
    focal_length_mm = 4.5
    laser_1_origin = np.array([0.05, 0, 0])
    laser_1_axis = np.array([0, 0, 1])

    plane_normal = np.array([0, 0, 1])
    plane_origin = np.array([0, 0, 5])

    laser_1_scalar = np.dot((plane_origin - laser_1_origin), plane_normal) / np.dot(
        laser_1_axis, plane_normal
    )
    laser_1_dot = laser_1_origin + laser_1_axis * laser_1_scalar
    laser_1_dot

    laser_1_projection = (
        -focal_length_mm
        / 1e3
        / laser_1_dot[2]
        * laser_1_dot[0:2]
        / (pixel_pitch_mm / 1e3)
    )  # in pixels
    laser_1_projection

    world_coordinate = compute_world_point(
        laser_origin=laser_1_origin,
        laser_axis=laser_1_axis,
        camera_params=(
            focal_length_mm,
            sensor_size_px[0],
            sensor_size_px[1],
            pixel_pitch_mm,
        ),
        image_coordinate=laser_1_projection,
    )
    print(world_coordinate)
    assert world_coordinate == 5.0


if __name__ == "__main__":
    test_run()
