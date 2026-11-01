import threading


def nurse_claims_until_empty(worklist, nurse_id, claimed_ids):
    while True:
        patient = worklist.claim_next(nurse_id)
        if patient is None:
            return
        claimed_ids.append(patient.patient_id)


def nurses_claim_concurrently(worklist, nurse_ids):
    claimed_by_nurse = {nurse_id: [] for nurse_id in nurse_ids}
    threads = [
        threading.Thread(target=nurse_claims_until_empty, args=(worklist, nurse_id, claimed_by_nurse[nurse_id]))
        for nurse_id in nurse_ids
    ]

    # Every thread is started before waiting for any of them, so the nurses really work at the same time
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    return claimed_by_nurse