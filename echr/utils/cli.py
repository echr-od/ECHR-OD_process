from rich.progress import ProgressColumn

TAB_SIZE = 8
TAB = " " * TAB_SIZE

class StatusColumn(ProgressColumn):
    def __init__(self, statuses, progress_style=None):
        super().__init__()
        self.statuses = statuses
        self.progress_style = progress_style

    def render(self, task: "Task"):
        if task.fields.get('rc') is not None:
            task.completed = task.total  # Trigger the end of the task
        label = self.statuses.get(task.fields.get('rc'))
        return label

def strfdelta(tdelta, fmt):
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    return fmt.format(**d)