import React, { useState, useEffect } from 'react';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { AlertTriangle, Users, TrendingUp, Phone, Activity } from 'lucide-react';

const SUPABASE_URL = "https://qpwwceigajtigvhpmbpg.supabase.co";
const SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFwd3djZWlnYWp0aWd2aHBtYnBnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzUwNzA3NzQsImV4cCI6MjA1MDY0Njc3NH0.iq_WCYhKFrEukGWTmO1DdT-HLSEyM6jUXWvL9xLsLNQ";

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];
const CAPACITY = {
  'Rabat': 50000,
  'Tanger': 65000,
  'Agadir': 45000,
  'Casablanca': 70000,
  'Marrakech': 40000
};

function App() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(new Date());
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const response = await fetch(
        `${SUPABASE_URL}/rest/v1/affluence?select=*&order=timestamp.desc&limit=100`,
        {
          headers: {
            'apikey': SUPABASE_KEY,
            'Authorization': `Bearer ${SUPABASE_KEY}`
          }
        }
      );
      
      const result = await response.json();
      setData(result);
      setLastUpdate(new Date());
      
      const newAlerts = result
        .filter(r => r.nombre_supporters > (CAPACITY[r.stade] || 50000) * 0.8)
        .slice(0, 5);
      setAlerts(newAlerts);
      
      setLoading(false);
    } catch (error) {
      console.error('Erreur Supabase:', error);
      setLoading(false);
    }
  };

  const latestByStade = data.reduce((acc, curr) => {
    if (!acc[curr.stade] || new Date(curr.timestamp) > new Date(acc[curr.stade].timestamp)) {
      acc[curr.stade] = curr;
    }
    return acc;
  }, {});

  const stadeStats = Object.values(latestByStade).map(s => ({
    name: s.stade,
    supporters: s.nombre_supporters,
    capacity: CAPACITY[s.stade] || 50000,
    taux: Math.round((s.nombre_supporters / (CAPACITY[s.stade] || 50000)) * 100)
  }));

  const timeSeriesData = data.slice(0, 30).reverse().map(d => ({
    time: new Date(d.timestamp).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }),
    [d.stade]: d.nombre_supporters
  }));

  const totalSupporters = stadeStats.reduce((sum, s) => sum + s.supporters, 0);
  const avgOccupancy = Math.round(stadeStats.reduce((sum, s) => sum + s.taux, 0) / stadeStats.length);
  const criticalStades = stadeStats.filter(s => s.taux > 80).length;

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', background: 'linear-gradient(135deg, #166534 0%, #991b1b 50%, #ca8a04 100%)' }}>
        <div style={{ color: 'white', fontSize: '24px' }}>Chargement des données CAN 2025...</div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #166534 0%, #991b1b 50%, #ca8a04 100%)', padding: '24px' }}>
      <div style={{ maxWidth: '1280px', margin: '0 auto' }}>
        {/* Header */}
        <div style={{ background: 'rgba(255,255,255,0.1)', backdropFilter: 'blur(12px)', borderRadius: '8px', padding: '24px', marginBottom: '24px', border: '1px solid rgba(255,255,255,0.2)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h1 style={{ fontSize: '36px', fontWeight: 'bold', color: 'white', marginBottom: '8px' }}>🏆 CAN 2025 - Surveillance Affluence</h1>
              <p style={{ color: '#bbf7d0' }}>Système de Gestion Temps Réel des Stades</p>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ color: 'white', fontSize: '14px' }}>Dernière mise à jour</div>
              <div style={{ color: '#fde047', fontFamily: 'monospace', fontSize: '18px' }}>{lastUpdate.toLocaleTimeString('fr-FR')}</div>
            </div>
          </div>
        </div>

        {/* KPIs */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '16px', marginBottom: '24px' }}>
          <div style={{ background: 'rgba(59,130,246,0.2)', backdropFilter: 'blur(12px)', borderRadius: '8px', padding: '24px', border: '1px solid rgba(147,197,253,0.3)' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div>
                <p style={{ color: '#bfdbfe', fontSize: '14px' }}>Total Supporters</p>
                <p style={{ color: 'white', fontSize: '30px', fontWeight: 'bold' }}>{totalSupporters.toLocaleString()}</p>
              </div>
              <Users color="#93c5fd" size={40} />
            </div>
          </div>

          <div style={{ background: 'rgba(34,197,94,0.2)', backdropFilter: 'blur(12px)', borderRadius: '8px', padding: '24px', border: '1px solid rgba(134,239,172,0.3)' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div>
                <p style={{ color: '#bbf7d0', fontSize: '14px' }}>Taux Moyen</p>
                <p style={{ color: 'white', fontSize: '30px', fontWeight: 'bold' }}>{avgOccupancy}%</p>
              </div>
              <TrendingUp color="#86efac" size={40} />
            </div>
          </div>

          <div style={{ background: 'rgba(239,68,68,0.2)', backdropFilter: 'blur(12px)', borderRadius: '8px', padding: '24px', border: '1px solid rgba(252,165,165,0.3)' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div>
                <p style={{ color: '#fecaca', fontSize: '14px' }}>Stades Critiques</p>
                <p style={{ color: 'white', fontSize: '30px', fontWeight: 'bold' }}>{criticalStades}</p>
              </div>
              <AlertTriangle color="#fca5a5" size={40} />
            </div>
          </div>

          <div style={{ background: 'rgba(168,85,247,0.2)', backdropFilter: 'blur(12px)', borderRadius: '8px', padding: '24px', border: '1px solid rgba(216,180,254,0.3)' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div>
                <p style={{ color: '#e9d5ff', fontSize: '14px' }}>Stades Actifs</p>
                <p style={{ color: 'white', fontSize: '30px', fontWeight: 'bold' }}>{stadeStats.length}</p>
              </div>
              <Activity color="#d8b4fe" size={40} />
            </div>
          </div>
        </div>

        {/* Alertes */}
        {alerts.length > 0 && (
          <div style={{ background: 'rgba(239,68,68,0.2)', backdropFilter: 'blur(12px)', borderRadius: '8px', padding: '24px', marginBottom: '24px', border: '1px solid rgba(252,165,165,0.3)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
              <Phone color="#fca5a5" size={24} />
              <h2 style={{ fontSize: '24px', fontWeight: 'bold', color: 'white' }}>Alertes SMS Twilio Actives</h2>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {alerts.map((alert, i) => (
                <div key={i} style={{ background: 'rgba(127,29,29,0.3)', borderRadius: '4px', padding: '12px', color: 'white' }}>
                  🚨 <strong>{alert.stade}</strong>: {alert.nombre_supporters.toLocaleString()} supporters 
                  ({Math.round((alert.nombre_supporters / (CAPACITY[alert.stade] || 50000)) * 100)}% capacité) 
                  - {new Date(alert.timestamp).toLocaleTimeString('fr-FR')}
                </div>
              ))}
            </div>
          </div>
        )}

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(500px, 1fr))', gap: '24px' }}>
          {/* Graphique en barres */}
          <div style={{ background: 'rgba(255,255,255,0.1)', backdropFilter: 'blur(12px)', borderRadius: '8px', padding: '24px', border: '1px solid rgba(255,255,255,0.2)' }}>
            <h2 style={{ fontSize: '24px', fontWeight: 'bold', color: 'white', marginBottom: '16px' }}>📊 Occupation Actuelle des Stades</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={stadeStats}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis dataKey="name" stroke="#fff" />
                <YAxis stroke="#fff" />
                <Tooltip contentStyle={{ backgroundColor: 'rgba(0,0,0,0.8)', border: 'none', borderRadius: '8px' }} />
                <Legend />
                <Bar dataKey="supporters" fill="#4ade80" name="Supporters" />
                <Bar dataKey="capacity" fill="#94a3b8" name="Capacité Max" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Diagramme circulaire */}
          <div style={{ background: 'rgba(255,255,255,0.1)', backdropFilter: 'blur(12px)', borderRadius: '8px', padding: '24px', border: '1px solid rgba(255,255,255,0.2)' }}>
            <h2 style={{ fontSize: '24px', fontWeight: 'bold', color: 'white', marginBottom: '16px' }}>🥧 Répartition des Supporters</h2>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={stadeStats}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={entry => `${entry.name}: ${entry.taux}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="supporters"
                >
                  {stadeStats.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: 'rgba(0,0,0,0.8)', border: 'none', borderRadius: '8px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Graphique temporel */}
          <div style={{ background: 'rgba(255,255,255,0.1)', backdropFilter: 'blur(12px)', borderRadius: '8px', padding: '24px', border: '1px solid rgba(255,255,255,0.2)', gridColumn: '1 / -1' }}>
            <h2 style={{ fontSize: '24px', fontWeight: 'bold', color: 'white', marginBottom: '16px' }}>📈 Évolution des 30 Dernières Minutes</h2>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={timeSeriesData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis dataKey="time" stroke="#fff" />
                <YAxis stroke="#fff" />
                <Tooltip contentStyle={{ backgroundColor: 'rgba(0,0,0,0.8)', border: 'none', borderRadius: '8px' }} />
                <Legend />
                {Object.keys(latestByStade).map((stade, i) => (
                  <Line key={stade} type="monotone" dataKey={stade} stroke={COLORS[i % COLORS.length]} strokeWidth={2} dot={{ r: 4 }} />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Tableau */}
          <div style={{ background: 'rgba(255,255,255,0.1)', backdropFilter: 'blur(12px)', borderRadius: '8px', padding: '24px', border: '1px solid rgba(255,255,255,0.2)', gridColumn: '1 / -1' }}>
            <h2 style={{ fontSize: '24px', fontWeight: 'bold', color: 'white', marginBottom: '16px' }}>📋 Vue Détaillée des Stades</h2>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', color: 'white', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.2)' }}>
                    <th style={{ textAlign: 'left', padding: '12px' }}>Stade</th>
                    <th style={{ textAlign: 'right', padding: '12px' }}>Supporters</th>
                    <th style={{ textAlign: 'right', padding: '12px' }}>Capacité</th>
                    <th style={{ textAlign: 'right', padding: '12px' }}>Taux</th>
                    <th style={{ textAlign: 'center', padding: '12px' }}>Statut</th>
                  </tr>
                </thead>
                <tbody>
                  {stadeStats.map((s, i) => (
                    <tr key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                      <td style={{ padding: '12px', fontWeight: '600' }}>{s.name}</td>
                      <td style={{ textAlign: 'right', padding: '12px' }}>{s.supporters.toLocaleString()}</td>
                      <td style={{ textAlign: 'right', padding: '12px' }}>{s.capacity.toLocaleString()}</td>
                      <td style={{ textAlign: 'right', padding: '12px' }}>
                        <span style={{ fontWeight: 'bold', color: s.taux > 80 ? '#fca5a5' : s.taux > 60 ? '#fde047' : '#86efac' }}>
                          {s.taux}%
                        </span>
                      </td>
                      <td style={{ textAlign: 'center', padding: '12px' }}>
                        {s.taux > 80 ? '🔴 Saturé' : s.taux > 60 ? '🟡 Moyen' : '🟢 Fluide'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div style={{ marginTop: '24px', textAlign: 'center', color: 'rgba(255,255,255,0.6)', fontSize: '14px' }}>
          <p>Système développé pour la CAN 2025 | Koyeb + Supabase + Twilio | YOLOv8</p>
        </div>
      </div>
    </div>
  );
}

export default App;
