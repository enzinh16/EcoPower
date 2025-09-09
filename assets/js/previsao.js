// Função para buscar a previsão do tempo
async function carregarPrevisao(plantId) {
    try {
        const response = await fetch(`http://localhost:5000/previsao-tempo?plantId=${plantId}`);
        if (!response.ok) {
            throw new Error("Erro ao buscar previsão do tempo");
        }

        const data = await response.json();

        // Exibe dados no console (debug)
        console.log(data);

        // Monta a previsão básica
        const previsaoDiv = document.getElementById("previsao");
        if (data.previsao && data.previsao.weather) {
            const cidade = data.previsao.name || "Localização";
            const temp = data.previsao.main.temp;
            const descricao = data.previsao.weather[0].description;

            previsaoDiv.innerHTML = `
                <h3>Previsão do Tempo</h3>
                <p><strong>Cidade:</strong> ${cidade}</p>
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

// Chama a função automaticamente com o plantId desejado
document.addEventListener("DOMContentLoaded", () => {
    const plantId = "7f9af1fc-3a9a-4779-a4c0-ca6ec87bd93a"; // pode ser dinâmico
    carregarPrevisao(plantId);
});
