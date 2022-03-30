from .video import Video


def get_subtitles(
    video_path: str,
    lang="eng",
    time_start="0:00",
    time_end="",
    conf_threshold=65,
    sim_threshold=90,
    tesseract_config="",
    roi=[[0, 1], [0, 1]],
    debug=False,
    num_jobs=None,
) -> str:
    v = Video(video_path)
    v.run_ocr(
        lang,
        time_start,
        time_end,
        conf_threshold,
        tesseract_config=tesseract_config,
        roi=roi,
        debug=debug,
        num_jobs=num_jobs,
    )
    return v.get_subtitles(sim_threshold)


def save_subtitles_to_file(
    video_path: str,
    file_path="subtitle.srt",
    lang="eng",
    time_start="0:00",
    time_end="",
    conf_threshold=65,
    sim_threshold=90,
    tesseract_config="",
    roi=[[0, 1], [0, 1]],
    debug=False,
    num_jobs=None,
) -> None:
    subs = get_subtitles(
               video_path,
               lang,
               time_start,
               time_end,
               conf_threshold,
               sim_threshold,
               tesseract_config=tesseract_config,
               roi=roi,
               debug=debug,
               num_jobs=num_jobs,
           )

    with open(file_path, "w+", encoding="utf-8") as f:
        f.write(subs)
