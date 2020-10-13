import { useState, useEffect } from 'react'

// Fetch hook scraped from the net; cleaned and improved
export const useFetch = (url, deferred = false) => {
    const [delayed, setDelayed] = useState(deferred)
    const [data, setData] = useState([])
    const [status, setStatus] = useState({loading: true, error: false})

    const fetchUrl = async () => {
        console.log(`fetch ${url}`)
        try {
            const response = await fetch(url, {
                method: 'GET',
                mode: 'cors',
                credentials: 'omit',
                headers: {
                    'Content-Type': 'application/json'
                    }})
            if (!response.ok) {
                setStatus({...status,
                           loading: false,
                           error: {status: response.status, text: response.text}
                          })
            } else {
                const json = await response.json()
                setData(json)
                setStatus({...status, loading: false})
            }
        } catch (exception) {
            /* nb. ublock can do nasty stuff that looks like cors errors :( */
            setStatus({...status, loading: false, error: {status: 0, text: 'exception', exception}})
        }
    }

    const start = () => setDelayed(false)

    useEffect(() => {
        if (!delayed)
            fetchUrl()
    }, [delayed])
    return [data, status, start]
}
