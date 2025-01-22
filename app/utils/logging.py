import json
import sys

from app.Config import ENV_PROJECT

LOG_FILE_PATH = "log.txt"


def loguru_sink_serializer(message):
    record = message.record
    simplified = {
        "@timestamp": f"{record['time'].strftime('%Y-%m-%dT%H:%M:%S.%fZ')[:-4]}Z",
        "level": record["level"].name,
        "projectName": ENV_PROJECT.APP_TITILE,
        "message": record["message"],
        "thread": record["thread"].name,
        "logger_name": record["name"],
        "process": record["process"].name,
    }

    if record["extra"].get("extra"):
        if "elapsedTimeMs" in record["extra"]["extra"]:
            simplified["elapsedTimeMs"] = record["extra"]["extra"]["elapsedTimeMs"]
        if "traceId" in record["extra"]["extra"]:
            if record["extra"]["extra"]["traceId"] != "None":
                simplified["traceId"] = record["extra"]["extra"]["traceId"]
        if "spanId" in record["extra"]["extra"]:
            simplified["spanId"] = record["extra"]["extra"]["spanId"]
        if "query" in record["extra"]["extra"]:
            simplified["query"] = record["extra"]["extra"]["query"]
    serialized = json.dumps(simplified)
    print(serialized, file=sys.stderr, end="\n")
    with open(LOG_FILE_PATH, "a") as log_file:
        log_file.write(json.dumps(serialized) + "\n")
