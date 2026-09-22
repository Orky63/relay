(() => {
  const endpoint = window.API_ENDPOINT || new URLSearchParams(location.search).get('api') || null
  const endpointInfo = document.getElementById('endpoint-info')
  endpointInfo.textContent = endpoint ? `Using API: ${endpoint}` : 'Using local demo data (no API configured)'

  const ticketsEl = document.getElementById('tickets')
  const form = document.getElementById('create-form')

  let tickets = [
    { id: '1', title: 'Website down', status: 'investigating' },
    { id: '2', title: 'Email delivery delay', status: 'open' }
  ]

  function render() {
    ticketsEl.innerHTML = ''
    tickets.forEach(t => {
      const div = document.createElement('div')
      div.className = `ticket status-${t.status}`
      div.innerHTML = `<strong>${t.title}</strong><div class="meta">ID: ${t.id} • Status: ${t.status}</div>`
      ticketsEl.appendChild(div)
    })
  }

  async function createTicket(data) {
    if (endpoint) {
      try {
        const res = await fetch(endpoint.replace(/\/$/, '') + '/tickets', {
          method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(data)
        })
        return await res.json()
      } catch (e) {
        alert('Failed to call API: '+e.message)
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
    const data = { title: fd.get('title'), status: fd.get('status') }
    const result = await createTicket(data)
    if (result && result.ticket) {
      if (!endpoint) { render() }
      form.reset()
    }
  })

  render()
})()
