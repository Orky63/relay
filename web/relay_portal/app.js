(() => {
    const endpoint = window.API_ENDPOINT || new URLSearchParams(location.search).get('api') || null
    const endpointInfo = document.getElementById('endpoint-info')
    endpointInfo.textContent = endpoint ? `Using API: ${endpoint}` : 'Using local demo data (no API configured)'

    const ticketsEl = document.getElementById('tickets')
    const form = document.getElementById('create-form')

    let tickets = [
        { id: '1', title: 'Website down', status: 'investigating', priority: 'P1' },
        { id: '2', title: 'Email delivery delay', status: 'open', priority: 'P2' }
    ]

    function render() {
        const activeP1s = tickets.filter(t => t.priority === 'P1' && ['open', 'investigating'].includes(t.status)).length
        const indicator = document.getElementById('p1-indicator')
        document.getElementById('p1-count').textContent = endpoint ? '—' : activeP1s
        document.getElementById('p1-description').textContent = endpoint
            ? 'Live P1 count unavailable'
            : `${activeP1s} active P1 ${activeP1s === 1 ? 'incident' : 'incidents'}`
        indicator.classList.toggle('has-incidents', !endpoint && activeP1s > 0)
        ticketsEl.innerHTML = ''
        tickets.forEach(t => {
            const div = document.createElement('div')
            div.className = `ticket status-${t.status}`
            const title = document.createElement('strong')
            title.textContent = t.title
            const meta = document.createElement('div')
            meta.className = 'meta'
            meta.textContent = `ID: ${t.id} • Priority: ${t.priority || 'Unassigned'} • Status: ${t.status}`
            div.append(title, meta)
            ticketsEl.appendChild(div)
        })
    }

    async function createTicket(data) {
        if (endpoint) {
            try {
                const res = await fetch(endpoint.replace(/\/$/, '') + '/tickets', {
                    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data)
                })
                return await res.json()
            } catch (e) {
                alert('Failed to call API: ' + e.message)
                return null
            }
        }
        // local demo
        const ticket = { id: Date.now().toString(), ...data }
        tickets.unshift(ticket)
        return { ticket }
    }

    form.addEventListener('submit', async (ev) => {
        ev.preventDefault()
        const fd = new FormData(form)
        const data = { title: fd.get('title'), status: fd.get('status'), priority: fd.get('priority') }
        const result = await createTicket(data)
        if (result && result.ticket) {
            if (!endpoint) { render() }
            form.reset()
        }
    })

    render()
})()
