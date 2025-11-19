import { useEffect, useState } from 'react';
import axios from 'axios';

function Admin() {
  const [status, setStatus] = useState(null);

  useEffect(() => {
    const fetchData = () => {
        axios.get('http://127.0.0.1:8000/infra/status')
          .then(res => setStatus(res.data))
          .catch(err => console.error(err));
    };
    fetchData();
    const interval = setInterval(fetchData, 3000); // 3초마다 자동 갱신
    return () => clearInterval(interval);
  }, []);

  if (!status) return <div style={{ padding: '20px' }}>Connecting to Physical AI System...</div>;

  return (
    <div>
      <h2 style={{ borderBottom: '2px solid #ff6b6b', paddingBottom: '10px', display: 'inline-block' }}>
        🏗️ Physical AI Infrastructure Monitor
      </h2>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px', marginTop: '20px' }}>
        {/* 트래픽 상태 */}
        <div style={{ background: 'white', padding: '25px', borderRadius: '15px', boxShadow: '0 4px 6px rgba(0,0,0,0.05)' }}>
            <h3 style={{ color: '#555', marginTop: 0 }}>Live Traffic</h3>
            <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: '#333' }}>{status.active_users} <span style={{ fontSize: '1rem', color: '#888' }}>Users</span></div>
            <div style={{ marginTop: '10px' }}>Total Posts: <strong>{status.total_posts}</strong></div>
        </div>

        {/* AI 제어 센터 */}
        <div style={{ background: '#20232a', color: 'white', padding: '25px', borderRadius: '15px', boxShadow: '0 4px 6px rgba(0,0,0,0.2)' }}>
            <h3 style={{ color: '#61dafb', marginTop: 0 }}>🤖 AI Control Center</h3>
            <div style={{ marginBottom: '15px' }}>
                <div style={{ fontSize: '0.9rem', opacity: 0.8 }}>Predicted Servers</div>
                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#61dafb' }}>{status.ai_prediction.needed_servers} <span style={{ fontSize: '1rem' }}>EA</span></div>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderTop: '1px solid #444', paddingTop: '15px' }}>
                <div>Temp: <strong>{status.ai_prediction.rack_temperature_avg}°C</strong></div>
                <div style={{ color: '#fbc02d' }}>Power: <strong>{status.ai_prediction.power_usage_watt} W</strong></div>
            </div>
        </div>
      </div>
    </div>
  );
}

export default Admin;