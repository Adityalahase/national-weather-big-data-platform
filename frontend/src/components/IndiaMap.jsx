import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
} from "react-leaflet";

import L from "leaflet";
import "leaflet/dist/leaflet.css";

// Fix Leaflet marker icons
delete L.Icon.Default.prototype._getIconUrl;

L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",

  iconUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",

  shadowUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

function IndiaMap({ events, onSelectEvent, timeline }) {
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm hover:shadow-md transition-shadow">

      <div className="mb-5 border-b border-slate-100 pb-4">
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-800">
          India Weather Map
        </h3>

        <p className="mt-1 text-xs font-medium text-slate-500">
          Live weather events across India
        </p>
      </div>

      <div className="h-[500px] rounded-lg overflow-hidden">

        <MapContainer
          center={[22.9734, 78.6569]}
          zoom={5}
          scrollWheelZoom={true}
          className="h-full w-full"
        >

          <TileLayer
            attribution='&copy; OpenStreetMap contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {events.map((event) => (
            <Marker
              key={event.id}
              position={[
                event.latitude,
                event.longitude,
              ]}
              eventHandlers={{
                click: () => onSelectEvent(event),
              }}
            >

              <Popup>

                <div className="min-w-[180px]">

                  <h4 className="font-bold text-slate-800 text-base">
                    {event.event_type}
                  </h4>

                  <p className="text-sm text-slate-600 mt-1">
                    {event.city}, {event.state}
                  </p>

                  <div className="border-t border-slate-200 my-2"></div>

                  <p className="text-sm">
                    <strong>Severity:</strong>{" "}
                    {event.severity}
                  </p>

                  <p className="text-sm">
                    <strong>Confidence:</strong>{" "}
                    {event.confidence_score}%
                  </p>

                  <p className="text-sm">
                    <strong>Status:</strong>{" "}
                    {event.verification_status}
                  </p>

                  <button
                    onClick={() => onSelectEvent(event)}
                    className="mt-3 w-full bg-blue-600 text-white text-sm px-3 py-2 rounded-lg"
                  >
                    View Intelligence
                  </button>

                </div>

              </Popup>

            </Marker>
          ))}

        </MapContainer>

      </div>

      {timeline}

    </section>
  );
}

export default IndiaMap;