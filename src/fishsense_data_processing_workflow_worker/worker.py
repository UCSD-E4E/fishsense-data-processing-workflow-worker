import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from temporalio.client import (
    Client,
    Schedule,
    ScheduleActionStartWorkflow,
    ScheduleIntervalSpec,
    ScheduleSpec,
    ScheduleState,
    TLSConfig,
)
from temporalio.worker import Worker

from fishsense_data_processing_workflow_worker.activities.group_dive_frames import (
    group_dive_frames,
)
from fishsense_data_processing_workflow_worker.config import configure_logging, settings
from fishsense_data_processing_workflow_worker.workflows.dive_frame_grouping_workflow import (
    DiveFrameGroupingWorkflow,
)

TASK_QUEUE_NAME = "fishsense_data_processing_queue"


async def schedule_workflows(_: Client):
    """Schedule workflows for the worker."""


async def main():
    """Main entry point for the worker."""

    configure_logging()
    log = logging.getLogger()

    tls_config: TLSConfig | None = None
    if settings.temporal.tls:
        with Path(settings.temporal.client_cert).open("rb") as f:
            client_cert = f.read()
        with Path(settings.temporal.client_private_key).open("rb") as f:
            client_private_key = f.read()

        server_root_ca_cert: bytes | None = None
        if "server_root_ca_cert" in settings.temporal:
            with Path(settings.temporal.server_root_ca_cert).open("rb") as f:
                server_root_ca_cert = f.read()

        tls_config = TLSConfig(
            client_cert=client_cert,
            client_private_key=client_private_key,
            server_root_ca_cert=server_root_ca_cert,
            domain=settings.temporal.domain if "domain" in settings.temporal else None,
        )

    client = await Client.connect(
        f"{settings.temporal.host}:{settings.temporal.port}", tls=tls_config
    )

    with ThreadPoolExecutor(max_workers=settings.general.max_workers) as executor:
        worker = Worker(
            client,
            task_queue=TASK_QUEUE_NAME,
            workflows=[DiveFrameGroupingWorkflow],
            activity_executor=executor,
            activities=[group_dive_frames],
        )

        worker_task = worker.run()
        log.info("Worker started, scheduling workflows...")

        await schedule_workflows(client)
        await worker_task


def run():
    """Run the worker."""
    asyncio.run(main())
