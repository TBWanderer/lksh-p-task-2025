document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('versusForm');
    if (!form) return;
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const player1Id = document.getElementById('player1Select').value;
        const player2Id = document.getElementById('player2Select').value;
        
        if (!player1Id || !player2Id) return;
        
        try {
            const response = await fetch(`/versus?player1_id=${player1Id}&player2_id=${player2Id}`);
            const data = await response.json();
            
            if (data.error) {
                alert(data.error);
                return;
            }
            
            document.getElementById('matchCount').textContent = data.match_count;
            document.getElementById('result').style.display = 'block';
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to load player matchup');
        }
    });
});
