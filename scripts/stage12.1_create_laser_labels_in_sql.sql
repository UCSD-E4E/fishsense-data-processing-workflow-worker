INSERT INTO laserlabel (
	label_studio_task_id,
	x,
	y,
	label,
	image_id,
	user_id,
	updated_at,
	completed,
	label_studio_json,
	label_studio_project_id,
	superseded
)
SELECT label_studio_task_id,
	laser_x,
	laser_y,
	laser_label,
	image_id,
	user_id,
	updated_at,
	completed,
	label_studio_json,
	label_studio_project_id,
	FALSE AS superseded
FROM specieslabel
JOIN image on image.id = specieslabel.image_id
JOIN dive on dive.id = image.dive_id
WHERE image.is_canonical
AND dive.id = 383