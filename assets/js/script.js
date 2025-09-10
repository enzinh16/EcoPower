// Primeiro script: carregarDados
async function carregarDados() {
    try {
        const resposta = await fetch('http://localhost:5000/detalhes-usina?plantId=7f9af1fc-3a9a-4779-a4c0-ca6ec87bd93a');
        const resposta2 = await fetch('http://localhost:5000/detalhes-monitor?plantId=7f9af1fc-3a9a-4779-a4c0-ca6ec87bd93a');

        const dados = await resposta.json();
        const dados2 = await resposta2.json();

        const container = document.getElementById('conteudo');

        if (
            dados?.data?.info?.address &&
            dados?.data?.info?.stationname &&
            dados?.data?.info?.powerstation_id &&
            dados2?.data?.info?.latitude &&
            dados2?.data?.info?.longitude &&
            dados?.data?.soc?.[0]?.sn &&
            dados?.data?.soc?.[0]?.power !== undefined &&
            dados?.data?.soc?.[1]?.sn &&
            dados?.data?.soc?.[1]?.power !== undefined
        ) {
            container.innerHTML = `
            <div class="kpis">
                <div class="kpi">
                    <h3>Detalhes da Planta</h3>
                    <p>Nome: ${dados.data.info.stationname}</p>
                    <p>Capacidade: ${dados.data.info.capacity} kW</p>
                    <p>ID: ${dados.data.info.powerstation_id}</p>
                    <p>Endereço: ${dados.data.info.address}</p>
                </div>
            </div>
            <div class="kpis">
                <div class="kpi">
                    <h3>Bateria 1</h3>
                    <p>SN: ${dados.data.soc[0].sn}</p>
                    <p>Carga: ${dados.data.soc[0].power}%</p>
                </div>
                <div class="kpi">
                    <h3>Bateria 2</h3>
                    <p>SN: ${dados.data.soc[1].sn}</p>
                    <p>Carga: ${dados.data.soc[1].power}%</p>
                </div>
            </div>

            <p><strong>Latitude:</strong> ${dados2.data.info.latitude}</p>
            <p><strong>Longitude:</strong> ${dados2.data.info.longitude}</p>
            `;

            // ✅ Chama a previsão do tempo somente depois de carregar os dados
            const plantId = dados.data.info.powerstation_id;
            carregarPrevisao(plantId);

        } else {
            console.log("⏳ Dados ainda incompletos, aguardando...");
            setTimeout(carregarDados, 2000); // tenta de novo em 2s
        }

    } catch (erro) {
        console.error('Erro ao buscar ou processar o JSON:', erro);
    }
}

// Segundo script: carregarPrevisao
async function carregarPrevisao(plantId) {
    try {
        const response = await fetch(`http://localhost:5000/previsao-tempo?plantId=${plantId}`);
        if (!response.ok) throw new Error("Erro ao buscar previsão do tempo");

        const data = await response.json();

        const previsaoDiv = document.getElementById("previsao");
        if (data.previsao && data.previsao.weather) {
            const temp = data.previsao.main.temp;
            const descricao = data.previsao.weather[0].description;

            previsaoDiv.innerHTML = `
                <h3>Previsão do Tempo</h3>
                <p><strong>Temperatura:</strong> ${temp} °C</p>
                <p><strong>Condição:</strong> ${descricao}</p>
            `;
        } else {
            previsaoDiv.innerHTML = "<p>Não foi possível carregar a previsão.</p>";
        }
    } catch (error) {
        console.error(error);
        document.getElementById("previsao").innerHTML =
            "<p>Erro ao carregar previsão do tempo.</p>";
    }
}

// Executa quando a página carregar
document.addEventListener("DOMContentLoaded", carregarDados);