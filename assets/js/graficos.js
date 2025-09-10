async function carregarDados() {
    const fixedDate = "2025-09-09"; // Data fixa para teste
    const serialNumber = "53600ERN238W0001";
    const urlPac = `http://localhost:5000/dados?sn=${serialNumber}&col=Pac&date=${fixedDate}`;
    const urlCbattery1 = `http://localhost:5000/dados?sn=${serialNumber}&col=Cbattery1&date=${fixedDate}`;
    const urlEday = `http://localhost:5000/dados?sn=${serialNumber}&col=Eday&date=${fixedDate}`;

    try {
        // ---------- Bateria ----------
        const respBateria = await fetch(urlCbattery1);
        const jsonBateria = await respBateria.json();
        const dadosBateria = jsonBateria.data.column1;

        const xBateria = dadosBateria.map(item => item.date);       // eixo X
        const yBateria = dadosBateria.map(item => item.column);    // eixo Y

        const ctxBateria = document.getElementById('graficoBateria').getContext('2d');
        new Chart(ctxBateria, {
            type: 'line',
            data: {
                labels: xBateria,
                datasets: [{
                    label: 'Bateria (%)',
                    data: yBateria,
                    borderColor: 'green',
                    tension: 0.2,
                    pointRadius: 2
                }]
            },
            options: {
                responsive: true, scales: {
                    x: { type: 'time', time: { parser: 'dd/MM/yyyy HH:mm:ss', unit: 'hour', tooltipFormat: 'dd/MM/yyyy HH:mm' } },
                    y: { title: { display: true, text: 'Bateria (%)' } }
                }
            }
        });

        // ---------- Potência (Pac) ----------
        const respPac = await fetch(urlPac);
        const jsonPac = await respPac.json();
        const dadosPac = jsonPac.data.column1;

        const xPac = dadosPac.map(item => item.date);       // eixo X
        const yPac = dadosPac.map(item => item.column);    // eixo Y

        const ctxPac = document.getElementById('graficoPac').getContext('2d');
        new Chart(ctxPac, {
            type: 'line',
            data: {
                labels: xPac,
                datasets: [{
                    label: 'Potência (W)',
                    data: yPac,
                    borderColor: 'blue',
                    tension: 0.2,
                    pointRadius: 2
                }]
            },
            options: {
                responsive: true, scales: {
                    x: { type: 'time', time: { parser: 'dd/MM/yyyy HH:mm:ss', unit: 'hour', tooltipFormat: 'dd/MM/yyyy HH:mm' } },
                    y: { title: { display: true, text: 'Potência (W)' } }
                }
            }
        });

        // ---------- Energia do dia (Eday) ----------
        const respEday = await fetch(urlEday);
        const jsonEday = await respEday.json();
        const dadosEday = jsonEday.data.column1;

        const xEday = dadosEday.map(item => item.date);       // eixo X
        const yEday = dadosEday.map(item => item.column);    // eixo Y

        const ctxEday = document.getElementById('graficoEday').getContext('2d');
        new Chart(ctxEday, {
            type: 'line',
            data: {
                labels: xEday,
                datasets: [{
                    label: 'Energia do dia (kWh)',
                    data: yEday,
                    borderColor: 'orange',
                    tension: 0.2,
                    pointRadius: 2
                }]
            },
            options: {
                responsive: true, scales: {
                    x: { type: 'time', time: { parser: 'dd/MM/yyyy HH:mm:ss', unit: 'hour', tooltipFormat: 'dd/MM/yyyy HH:mm' } },
                    y: { title: { display: true, text: 'Energia do dia (kWh)' } }
                }
            }
        });

        // KPIs
        const container = document.getElementById('detalhes');
        const inicioBateria = yBateria[0] ?? "-";
        const fimBateria = yBateria[yBateria.length - 1] ?? "-";

        const valoresEday = dadosEday.map(item => item.column);

        let maiorPac = -Infinity;
        let horarioMaiorPac = "";

        dadosPac.forEach(item => {
            if(item.column > maiorPac){
                maiorPac = item.column;
                horarioMaiorPac = item.date;
            }
        });
        const horaMinuto = horarioMaiorPac.split(' ')[1];

        container.innerHTML = `
        <div class="kpis">
            <div class="kpi">
                <h3>Bateria</h3>
                <p>${inicioBateria}% → ${fimBateria}%</p>
            </div>
            <div class="kpi">
                <h3>Energia do dia</h3>
                <p>${Math.max(...valoresEday).toFixed(2)} kWh</p>
            </div>
            <div class="kpi">
                <h3>Pico de potência</h3>
                <p>${maiorPac.toFixed(2)} kW (${horaMinuto})</p>
            </div>
        </div>
        `;

    } catch (err) {
        console.error("Erro ao carregar JSON:", err);
    }
}
carregarDados();
