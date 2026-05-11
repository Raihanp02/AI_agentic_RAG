def update_progress(
    progress_store,
    job_id,
    **kwargs
):

    current = progress_store.get(job_id, {})

    current.update(kwargs)

    progress_store[job_id] = current