document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('statsForm');
    if (!form) return;
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const teamName = document.getElementById('teamSelect').value;
        if (!teamName) return;
        
        try {
            const response = await fetch(`/stats?team_name=${encodeURIComponent(teamName)}`);
            const data = await response.json();
            
            if (data.error) {
                alert(data.error);
                return;
            }
            
            document.getElementById('teamName').textContent = teamName;
            document.getElementById('wins').textContent = data.wins;
            document.getElementById('losses').textContent = data.losses;
            
            const goalDiff = data.goal_difference;
            document.getElementById('goalDiff').textContent = goalDiff > 0 ? `+${goalDiff}` : goalDiff;
            
            document.getElementById('result').style.display = 'block';
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to load team stats');
        }
    });
});
