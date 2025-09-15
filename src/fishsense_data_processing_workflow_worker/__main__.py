"""Entry point for the FishSense Data Processing Workflow Worker."""

import asyncio

from fishsense_data_processing_workflow_worker.worker import main

if __name__ == "__main__":
    asyncio.run(main())
