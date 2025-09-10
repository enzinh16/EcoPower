let chartBateria, chartPac, chartEday;

async function carregarDados(dataSelecionada) {
    const serialNumber = "53600ERN238W0001";
    const dataFormatada = dataSelecionada; // já está no formato "YYYY-MM-DD"

    const urlPac = `http://localhost:5000/dados?sn=${serialNumber}&col=Pac&date=${dataFormatada}`;
    const urlCbattery1 = `http://localhost:5000/dados?sn=${serialNumber}&col=Cbattery1&date=${dataFormatada}`;
    const urlEday = `http://localhost:5000/dados?sn=${serialNumber}&col=Eday&date=${dataFormatada}`;

    try {
        // ---------- Bateria ----------
        const respBateria = await fetch(urlCbattery1);
        const dadosBateria = (await respBateria.json()).data?.column1 || [];

        const dadosBateriaGrafico = dadosBateria.map(item => ({
            x: new Date(item.date),
            y: item.column
        }));

        const ctxBateria = document.getElementById('graficoBateria').getContext('2d');
        if (chartBateria) chartBateria.destroy();
        chartBateria = new Chart(ctxBateria, {
            type: 'line',
            data: { datasets: [{ label: 'Bateria (%)', data: dadosBateriaGrafico, borderColor: 'green', tension: 0.2, pointRadius: 2, spanGaps: true }] },
            options: {
                responsive: true,
                scales: {
                    x: { type: 'time', time: { unit: 'hour', tooltipFormat: 'HH:mm' } },
                    y: { title: { display: true, text: 'Bateria (%)' } }
                }
            }
        });

        // ---------- Pac ----------
        const respPac = await fetch(urlPac);
        const dadosPac = (await respPac.json()).data?.column1 || [];

        const dadosPacGrafico = dadosPac.map(item => ({
            x: new Date(item.date),
            y: item.column
        }));

        let maiorPac = dadosPac.length ? Math.max(...dadosPac.map(d => d.column)) : 0;
        let horarioMaiorPac = dadosPac.length ? dadosPac[dadosPac.map(d => d.column).indexOf(maiorPac)].date.split(' ')[1] : "-";

        const ctxPac = document.getElementById('graficoPac').getContext('2d');
        if (chartPac) chartPac.destroy();
        chartPac = new Chart(ctxPac, {
            type: 'line',
            data: { datasets: [{ label: 'Potência (W)', data: dadosPacGrafico, borderColor: 'blue', tension: 0.2, pointRadius: 2, spanGaps: true }] },
            options: {
                responsive: true,
                scales: {
                    x: { type: 'time', time: { unit: 'hour', tooltipFormat: 'HH:mm' } },
                    y: { title: { display: true, text: 'Potência (W)' } }
                }
            }
        });

        // ---------- Eday ----------
        const respEday = await fetch(urlEday);
        const dadosEday = (await respEday.json()).data?.column1 || [];

        const dadosEdayGrafico = dadosEday.map(item => ({
            x: new Date(item.date),
            y: item.column
        }));

        const ctxEday = document.getElementById('graficoEday').getContext('2d');
        if (chartEday) chartEday.destroy();
        chartEday = new Chart(ctxEday, {
            type: 'line',
            data: { datasets: [{ label: 'Energia do dia (kWh)', data: dadosEdayGrafico, borderColor: 'orange', tension: 0.2, pointRadius: 2, spanGaps: true }] },
            options: {
                responsive: true,
                scales: {
                    x: { type: 'time', time: { unit: 'hour', tooltipFormat: 'HH:mm' } },
                    y: { title: { display: true, text: 'Energia do dia (kWh)' } }
                }
            }
        });

        // ---------- KPIs ----------
        const container = document.getElementById('detalhes');
        const inicioBateria = dadosBateria.length ? dadosBateria[0].column : "-";
        const fimBateria = dadosBateria.length ? dadosBateria[dadosBateria.length - 1].column : "-";
        const maxEday = dadosEday.length ? Math.max(...dadosEday.map(d => d.column)) : 0;

        container.innerHTML = `
        <div class="kpis">
            <div class="kpi">
                <h3>Bateria</h3>
                <p>${inicioBateria}% → ${fimBateria}%</p>
            </div>
            <div class="kpi">
                <h3>Energia do dia</h3>
                <p>${maxEday.toFixed(2)} kWh</p>
            </div>
            <div class="kpi">
                <h3>Pico de potência</h3>
                <p>${maiorPac.toFixed(2)} kW (${horarioMaiorPac})</p>
            </div>
        </div>`;
        
    } catch (err) {
        console.error("Erro ao carregar JSON:", err);
    }
}

// Inicializa
document.addEventListener("DOMContentLoaded", () => {
    const inputData = document.getElementById("dataFiltro");
    const btnFiltrar = document.getElementById("btnFiltrar");

    carregarDados(inputData.value);

    btnFiltrar.addEventListener("click", () => {
        carregarDados(inputData.value);
    });
});
