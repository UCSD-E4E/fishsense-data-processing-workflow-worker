from datetime import datetime, timedelta
from typing import Iterable

from pydantic import BaseModel
from temporalio import workflow

from fishsense_data_processing_workflow_worker.models import Dive, Image


@workflow.defn
class DiveFrameClusteringWorkflow:
    # pylint: disable=too-few-public-methods
    @workflow.run
    async def run(
        self, dive: Dive, images: Iterable[Image]
    ) -> Iterable[Iterable[Image]]:
        workflow.logger.info("here")

        return await workflow.execute_activity(
            "cluster_dive_frames",
            args=(images,),
            schedule_to_close_timeout=timedelta(minutes=10),
        )
