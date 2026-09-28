function formatTimelineTime(time) {
  return new Date(time).toLocaleString([], {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function TimelineSlider({
  currentTime,
  earliestTime,
  latestTime,
  isPlaying,
  currentEventCount,
  totalEventCount,
  onTimeChange,
  onPlay,
  onPause,
  onReset,
}) {
  return (
    <section className="mt-6 border-t border-slate-200 pt-6" aria-label="Historical weather timeline">
      <div className="flex flex-wrap items-center justify-between gap-3 mb-5">
        <div>
          <h4 className="text-sm font-bold uppercase tracking-wider text-slate-800">Historical Weather Timeline</h4>
          <p className="mt-1 text-xs font-medium text-slate-500">
            Current Events: {currentEventCount} / Total Events: {totalEventCount}
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {isPlaying ? (
            <button
              type="button"
              onClick={onPause}
              className="rounded-lg bg-slate-800 px-4 py-2 text-xs font-bold uppercase tracking-wider text-white transition hover:bg-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-sm"
            >
              ⏸ Pause
            </button>
          ) : (
            <button
              type="button"
              onClick={onPlay}
              className="rounded-lg bg-blue-600 px-4 py-2 text-xs font-bold uppercase tracking-wider text-white transition hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-sm"
            >
              ▶ Play
            </button>
          )}
          <button
            type="button"
            onClick={onReset}
            className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-xs font-bold uppercase tracking-wider text-slate-700 transition hover:bg-slate-50 hover:border-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-sm"
          >
            ↺ Reset
          </button>
        </div>
      </div>

      <div className="mt-4">
        <input
          type="range"
          min={earliestTime}
          max={latestTime}
          step={1000}
          value={currentTime}
          onChange={(event) => onTimeChange(Number(event.target.value))}
          className="h-2 w-full cursor-pointer accent-blue-600"
          aria-label="Select historical weather time"
        />
        <div className="mt-2 flex justify-between text-xs text-slate-400">
          <span>{formatTimelineTime(earliestTime)}</span>
          <span>{formatTimelineTime(latestTime)}</span>
        </div>
      </div>

      <p className="mt-4 text-center text-sm font-semibold text-slate-700">
        {formatTimelineTime(currentTime)}
      </p>
    </section>
  );
}

export default TimelineSlider;
