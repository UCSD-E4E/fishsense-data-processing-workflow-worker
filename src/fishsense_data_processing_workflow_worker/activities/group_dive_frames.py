from typing import Iterator

from sklearn.cluster import HDBSCAN
from temporalio import activity

from fishsense_data_processing_workflow_worker.models import Dive, Image


@activity.defn
async def group_dive_frames(images: Iterator[Image]):
    """Group dive frames into clusters based on their timestamps.

    Args:
        images (Iterator[Image]): An iterator of Image objects to be grouped.

    Returns:
        list[list[Image]]: A list of clusters, where each cluster is a list of Image objects.
    """
    # Convert the iterator to a list for processing
    image_list = list(images)

    if not image_list:
        return []

    # Extract timestamps and convert them to seconds since epoch
    timestamps = [
        img.taken_datetime.timestamp() if img.taken_datetime else 0
        for img in image_list
    ]

    # Reshape timestamps for DBSCAN
    X = [[ts] for ts in timestamps]

    # Define DBSCAN parameters
    min_samples = 2  # Minimum number of images to form a cluster

    activity.logger.info(f"Clustering {len(image_list)} images")

    # Perform HDBSCAN clustering
    db = HDBSCAN(min_cluster_size=min_samples).fit(X)
    labels = db.labels_

    # Group images by their cluster labels
    clusters = {}
    for label, img in zip(labels, image_list):
        if label == -1:
            continue  # Ignore noise points
        if label not in clusters:
            clusters[label] = []
        clusters[label].append(img)

    return list(clusters.values())
