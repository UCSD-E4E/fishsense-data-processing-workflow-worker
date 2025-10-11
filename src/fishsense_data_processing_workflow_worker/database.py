"""Database interaction module for FishSense API Workflow Worker."""

from __future__ import annotations

from typing import Iterable

from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel, and_, select
from sqlmodel.ext.asyncio.session import AsyncSession

from fishsense_data_processing_workflow_worker.models.camera import Camera
from fishsense_data_processing_workflow_worker.models.dive import Dive
from fishsense_data_processing_workflow_worker.models.dive_frame_cluster import (
    DiveFrameCluster,
    DiveFrameClusterImageMapping,
)
from fishsense_data_processing_workflow_worker.models.dive_slate import DiveSlate
from fishsense_data_processing_workflow_worker.models.head_tail_label import (
    HeadTailLabel,
)
from fishsense_data_processing_workflow_worker.models.image import Image
from fishsense_data_processing_workflow_worker.models.laser_label import LaserLabel
from fishsense_data_processing_workflow_worker.models.user import User


class Database:
    # pylint: disable=too-many-public-methods
    """Database interaction class for FishSense API Workflow Worker."""

    def __init__(self, database_url: str):
        self.engine = create_async_engine(database_url)

    async def init_database(self) -> None:
        """Initialize the database by creating all tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

    async def select_camera_by_id(
        self, camera_id: int, session: AsyncSession | None = None
    ) -> Camera | None:
        """Select a camera by its ID."""
        query = select(Camera).where(Camera.id == camera_id)

        if session is None:
            async with AsyncSession(self.engine) as session:
                result = await session.exec(query)
        else:
            result = await session.exec(query)

        return result.one_or_none()

    async def select_camera_by_serial_number(
        self, serial_number: str, session: AsyncSession | None = None
    ) -> Camera | None:
        """Select a camera by its serial number."""
        query = select(Camera).where(Camera.serial_number == serial_number)

        if session is None:
            async with AsyncSession(self.engine) as session:
                result = await session.exec(query)
        else:
            result = await session.exec(query)

        return result.one_or_none()

    async def select_dive_by_id(
        self, dive_id: int, session: AsyncSession | None = None
    ) -> Dive | None:
        """Select a dive by its ID."""
        query = select(Dive).where(Dive.id == dive_id)
        if session is None:
            async with AsyncSession(self.engine) as session:
                result = await session.exec(query)
        else:
            result = await session.exec(query)

        return result.one_or_none()

    async def select_dive_by_path(
        self, dive_path: str, session: AsyncSession | None = None
    ) -> Dive | None:
        """Select a dive by its path."""
        query = select(Dive).where(Dive.path == dive_path)

        if session is None:
            async with AsyncSession(self.engine) as session:
                result = await session.exec(query)
        else:
            result = await session.exec(query)

        return result.one_or_none()

    async def select_dives(self, session: AsyncSession | None = None) -> Iterable[Dive]:
        """Select all dives ordered by dive datetime."""
        query = select(Dive).order_by(Dive.dive_datetime)

        if session is None:
            async with AsyncSession(self.engine) as session:
                result = await session.exec(query)
        else:
            result = await session.exec(query)

        return result.all()

    async def select_dives_by_ids(
        self, dive_ids: Iterable[int], session: AsyncSession | None = None
    ) -> Iterable[Dive]:
        """Select dives by their IDs."""
        query = (
            select(Dive)
            .where(Dive.id.in_(dive_ids))  # pylint: disable=no-member
            .order_by(Dive.dive_datetime)
        )

        if session is None:
            async with AsyncSession(self.engine) as session:
                result = await session.exec(query)
        else:
            result = await session.exec(query)

        return result.all()

    async def select_dives_to_process(
        self, session: AsyncSession | None = None
    ) -> Iterable[Dive]:
        """Select dives that need processing."""
        query = select(Dive).order_by(Dive.dive_datetime)

        if session is None:
            async with AsyncSession(self.engine) as session:
                result = await session.exec(query)
        else:
            result = await session.exec(query)

        return result.all()

    async def select_dive_slate_by_name(
        self, name: str, session: AsyncSession | None = None
    ) -> DiveSlate | None:
        """Select a dive slate by its name."""
        query = select(DiveSlate).where(DiveSlate.name == name)

        if session is None:
            async with AsyncSession(self.engine) as session:
                result = await session.exec(query)
        else:
            result = await session.exec(query)

        return result.one_or_none()

    async def select_head_tail_labels_by_task_id(
        self, task_id: int, session: AsyncSession | None = None
    ) -> HeadTailLabel | None:
        """Select head-tail labels by their Label Studio task ID."""
        query = select(HeadTailLabel).where(
            HeadTailLabel.label_studio_task_id == task_id
        )

        if session is None:
            async with AsyncSession(self.engine) as session:
                result = await session.exec(query)
        else:
            result = await session.exec(query)

        return result.one_or_none()

    async def select_head_tail_labels(
        self, session: AsyncSession | None = None
    ) -> Iterable[HeadTailLabel]:
        """Select all head-tail labels."""
        query = select(HeadTailLabel)

        if session is None:
            async with AsyncSession(self.engine) as session:
                result = await session.exec(query)
        else:
            result = await session.exec(query)

        return result.all()

    async def select_head_tail_labels_by_image_ids(
        self, image_ids: Iterable[int], session: AsyncSession | None = None
    ) -> Iterable[HeadTailLabel]:
        """Select head-tail labels by their image IDs."""
        query = select(HeadTailLabel).where(
            HeadTailLabel.image_id.in_(image_ids)  # pylint: disable=no-member
        )

        if session is None:
            async with AsyncSession(self.engine) as session:
                result = await session.exec(query)
        else:
            result = await session.exec(query)

        return result.all()

    async def select_image_by_checksum(
        self, image_checksum: str, session: AsyncSession | None = None
    ) -> Image | None:
        """Select a canonical image by its checksum."""
        query = select(Image).where(
            and_(Image.checksum == image_checksum, Image.is_canonical)
        )

        if session is None:
            async with AsyncSession(self.engine) as session:
                result = await session.exec(query)
        else:
            result = await session.exec(query)

        return result.one_or_none()

    async def select_image_by_path(
        self, path: str, session: AsyncSession | None = None
    ) -> Image | None:
        """Select an image by its path."""
        query = select(Image).where(Image.path == path)

        if session is None:
            async with AsyncSession(self.engine) as session:
                result = await session.exec(query)
        else:
            result = await session.exec(query)

        return result.one_or_none()

    async def select_images_by_checksum(
        self, image_checksum: Iterable[str], session: AsyncSession | None = None
    ) -> Iterable[Image]:
        """Select canonical images by their checksums."""
        query = select(Image).where(
            and_(
                Image.checksum.in_(image_checksum),  # pylint: disable=no-member
                Image.is_canonical,
            )
        )

        if session is None:
            async with AsyncSession(self.engine) as session:
                result = await session.exec(query)
        else:
            result = await session.exec(query)

        return result.all()

    async def select_images_by_dive_id(
        self, dive_id: int, session: AsyncSession | None = None
    ) -> Iterable[Image]:
        """Select images by their dive ID."""
        query = select(Image).where(Image.dive_id == dive_id).order_by(Image.path)

        if session is None:
            async with AsyncSession(self.engine) as session:
                result = await session.exec(query)
        else:
            result = await session.exec(query)

        return result.all()

    async def select_images_by_dive_ids(
        self, dive_ids: Iterable[int], session: AsyncSession | None = None
    ) -> Iterable[Image]:
        """Select images by their dive IDs."""
        query = (
            select(Image)
            .where(Image.dive_id.in_(dive_ids))  # pylint: disable=no-member
            .order_by(Image.path)
        )
        if session is None:
            async with AsyncSession(self.engine) as session:
                result = await session.exec(query)
        else:
            result = await session.exec(query)

        return result.all()

    async def select_images_by_ids(
        self, image_ids: Iterable[int], session: AsyncSession | None = None
    ) -> Iterable[Image]:
        """Select images by their IDs."""
        query = select(Image).where(
            Image.id.in_(image_ids)  # pylint: disable=no-member
        )

        if session is None:
            async with AsyncSession(self.engine) as session:
                result = await session.exec(query)
        else:
            result = await session.exec(query)

        return result.all()

    async def select_laser_label_by_image_id(
        self, image_id: int, session: AsyncSession | None = None
    ) -> LaserLabel | None:
        """Select a laser label by its image ID."""
        query = select(LaserLabel).where(LaserLabel.image_id == image_id)

        if session is None:
            async with AsyncSession(self.engine) as session:
                result = await session.exec(query)
        else:
            result = await session.exec(query)

        return result.one_or_none()

    async def select_laser_label_by_task_id(
        self, task_id: int, session: AsyncSession | None = None
    ) -> LaserLabel | None:
        """Select a laser label by its Label Studio task ID."""
        query = select(LaserLabel).where(LaserLabel.label_studio_task_id == task_id)

        if session is None:
            async with AsyncSession(self.engine) as session:
                result = await session.exec(query)
        else:
            result = await session.exec(query)

        return result.one_or_none()

    async def select_laser_labels(
        self, session: AsyncSession | None = None
    ) -> Iterable[LaserLabel]:
        """Select all laser labels."""
        query = select(LaserLabel)

        if session is None:
            async with AsyncSession(self.engine) as session:
                result = await session.exec(query)
        else:
            result = await session.exec(query)

        return result.all()

    async def select_laser_labels_by_image_ids(
        self, image_ids: Iterable[int], session: AsyncSession | None = None
    ) -> Iterable[LaserLabel]:
        """Select laser labels by their image IDs."""
        query = select(LaserLabel).where(
            LaserLabel.image_id.in_(image_ids)  # pylint: disable=no-member
        )

        if session is None:
            async with AsyncSession(self.engine) as session:
                result = await session.exec(query)
        else:
            result = await session.exec(query)

        return result.all()

    async def select_user_by_email(
        self, email: str, session: AsyncSession | None = None
    ) -> User | None:
        """Select a user by their email address."""
        query = select(User).where(User.email == email)

        if session is None:
            async with AsyncSession(self.engine) as session:
                result = await session.exec(query)
        else:
            result = await session.exec(query)

        return result.one_or_none()

    async def select_user_by_label_studio_id(
        self, label_studio_id: str, session: AsyncSession | None = None
    ) -> User | None:
        """Select a user by their Label Studio ID."""
        query = select(User).where(User.label_studio_id == label_studio_id)

        if session is None:
            async with AsyncSession(self.engine) as session:
                result = await session.exec(query)
        else:
            result = await session.exec(query)

        return result.one_or_none()

        return result.one_or_none()

    async def select_dive_frame_clusters(
        self, session: AsyncSession | None = None
    ) -> Iterable[DiveFrameCluster]:
        """Select all dive frame clusters."""
        query = select(DiveFrameCluster)

        if session is None:
            async with AsyncSession(self.engine) as session:
                result = await session.exec(query)
        else:
            result = await session.exec(query)

        return result.all()

    async def select_dive_frame_cluster_image_mappings_by_cluster_id(
        self, cluster_id: int, session: AsyncSession | None = None
    ) -> Iterable[DiveFrameClusterImageMapping]:
        """Select all image mappings for a given dive frame cluster ID."""
        query = select(DiveFrameClusterImageMapping).where(
            DiveFrameClusterImageMapping.dive_frame_cluster_id == cluster_id
        )

        if session is None:
            async with AsyncSession(self.engine) as session:
                result = await session.exec(query)
        else:
            result = await session.exec(query)

        return result.all()
