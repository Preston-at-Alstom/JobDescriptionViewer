


def clear_duplicates(jd):
    for entry, job in enumerate(jd):
        # Start after first entry (0)
        if entry > 0:
            # compare job number and operating days with previous entry
            current_job = job
            previous_job = jd[entry -1  ]

            
            if  current_job.job_number == previous_job.job_number and \
                current_job.operating_days == previous_job.operating_days and \
                current_job.trips == []   :
                
                jd.pop(entry)
                

    return jd