import ast
import importlib
import json


def push_to_queue(queryset) -> str:
    msg = ""
    for task_res in queryset:
        if task_res.status != "FAILURE":
            msg += f'{task_res.task_id} => Skipped. Not in "FAILURE" State<br>'
            continue
        try:
            task_actual_name = task_res.task_name.split(".")[-1]
            module_name = ".".join(task_res.task_name.split(".")[:-1])
            kwargs = json.loads(task_res.task_kwargs)
            if isinstance(kwargs, str):
                kwargs = kwargs.replace("'", '"')
                kwargs = json.loads(kwargs)
                if kwargs:
                    getattr(importlib.import_module(module_name), task_actual_name).apply_async(
                        kwargs=kwargs, task_id=task_res.task_id
                    )
            if not kwargs:
                args = ast.literal_eval(ast.literal_eval(task_res.task_args))
                getattr(importlib.import_module(module_name), task_actual_name).apply_async(
                    args, task_id=task_res.task_id
                )
            msg += f"{task_res.task_id} - Successfully sent to queue for retry"
        except Exception as ex:
            msg += f"{task_res.task_id} - Unable to process. Error: {ex}"
    return msg
