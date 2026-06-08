def create_window_metric(
    session,
    data
):
    metric = WindowMetrics(**data)

    session.add(metric)

    session.commit()

    session.refresh(metric)

    return metric