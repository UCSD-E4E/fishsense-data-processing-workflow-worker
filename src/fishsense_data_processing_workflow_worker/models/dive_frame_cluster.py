from sqlmodel import Field, SQLModel


class DiveFrameCluster(SQLModel, table=True):
    """Model representing a cluster of frames within a dive."""

    id: int | None = Field(default=None, primary_key=True)

    dive_id: int | None = Field(default=None, foreign_key="dive.id")


class DiveFrameClusterImageMapping(SQLModel, table=True):
    """Association table mapping images to dive frame clusters."""

    dive_frame_cluster_id: int = Field(
        default=None, foreign_key="diveframecluster.id", primary_key=True
    )
    image_id: int = Field(default=None, foreign_key="image.id", primary_key=True)
