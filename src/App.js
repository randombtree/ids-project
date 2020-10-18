import React from 'react'

import { Map, TileLayer, Marker, Tooltip } from 'react-leaflet'
import './App.css'

import { useFetch } from './hooks'

const toLatLng = (property) =>
      [property.latitude, property.longitude]
function App() {
    const [properties, propertiesStatus, _propStart] = useFetch('/api/properties', false)
    if (propertiesStatus.loading)
        return <p>Loading ...</p>
    else if (propertiesStatus.error)
        return <p>Error loading properties</p>

    return (
        <div className="App">
          <Map
            id="mapElement"
            center={toLatLng(properties[Object.keys(properties)[0]])} // Center on first building
            zoom='13'
          >
            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution='&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
            />
            {
                Object.entries(properties)
                    .map(([buildingCode, p]) => (
                        <Marker key={buildingCode} position={toLatLng(p)}>
                          <Tooltip>{p.propertyName}</Tooltip>
                        </Marker>
                    ))

            }
          </Map>
        </div>
    );
}

export default App
