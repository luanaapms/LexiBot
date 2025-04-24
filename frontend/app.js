document.getElementById("submitBtn").addEventListener("click", async function() {
    const text = document.getElementById("inputText").value;
    const response = await fetch("http://localhost:8000/mentor", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ text: text })
    });
    const result = await response.json();
    
    // Exibir erros
    const errorsList = document.getElementById("errorsList");
    errorsList.innerHTML = '';
    result.errors.forEach(error => {
        const li = document.createElement("li");
        li.textContent = `Erro: ${error.original} → Correção: ${error.correction}`;
        errorsList.appendChild(li);
    });

    // Exibir explicações
    const explanationsList = document.getElementById("explanationsList");
    explanationsList.innerHTML = '';
    result.explanations.forEach(explanation => {
        const li = document.createElement("li");
        li.textContent = explanation;
        explanationsList.appendChild(li);
    });

    // Exibir exercícios
    const exercisesList = document.getElementById("exercisesList");
    exercisesList.innerHTML = '';
    result.exercises.forEach(exercise => {
        const li = document.createElement("li");
        li.textContent = exercise;
        exercisesList.appendChild(li);
    });
});
