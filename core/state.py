from multiprocessing import Manager

job_manager = Manager()
progress_dict = job_manager.dict()