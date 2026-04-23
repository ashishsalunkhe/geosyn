import argparse
import time

from celery.result import AsyncResult

from app.core.celery_app import celery_app
from app.workers.tasks import (
    run_alert_generation,
    run_clustering,
    run_market_sync,
    run_news_ingestion,
    run_nexus_sync,
)


def wait_for_task(task_id: str, poll_interval: float = 2.0) -> dict:
    while True:
        result = AsyncResult(task_id, app=celery_app)
        if result.status == "SUCCESS":
            return {"task_id": task_id, "status": result.status, "result": result.result}
        if result.status == "FAILURE":
            return {"task_id": task_id, "status": result.status, "error": str(result.result)}
        time.sleep(poll_interval)


def main():
    parser = argparse.ArgumentParser(description="Queue a full GeoSyn mesh sync through Celery.")
    parser.add_argument("--customer-id", help="Optional customer ID for alert generation.")
    parser.add_argument("--wait", action="store_true", help="Wait for each task to complete before continuing.")
    args = parser.parse_args()

    tasks = [
        ("market_sync", run_market_sync.delay()),
        ("news_ingestion", run_news_ingestion.delay(True)),
        ("clustering", run_clustering.delay()),
        ("nexus_sync", run_nexus_sync.delay()),
    ]

    if args.customer_id:
        tasks.append(("alert_generation", run_alert_generation.delay(args.customer_id)))

    for name, task in tasks:
        print(f"[queued] {name}: {task.id}")
        if args.wait:
            result = wait_for_task(task.id)
            print(result)


if __name__ == "__main__":
    main()
