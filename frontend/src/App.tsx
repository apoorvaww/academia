import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { ProfileEditor } from './components/ProfileEditor';
import { RecommendationList } from './components/RecommendationList';
import { CareerAgentChat } from './components/CareerAgentChat';
import { api } from './services/api';
import { StudentProfile, RecommendationItem, HealthResponse } from './types';
import { Loader2 } from 'lucide-react';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'profile' | 'recommendations' | 'agent'>('profile');
  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [recommendations, setRecommendations] = useState<RecommendationItem[]>([]);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [isLoadingProfile, setIsLoadingProfile] = useState(true);
  const [isLoadingRecs, setIsLoadingRecs] = useState(false);

  const fetchInitialData = async () => {
    setIsLoadingProfile(true);
    try {
      const [h, p] = await Promise.all([
        api.getHealth().catch(() => null),
        api.getProfile(1)
      ]);
      setHealth(h);
      setProfile(p);
      if (p) {
        fetchRecs(p.id);
      }
    } catch (err) {
      console.error('Error loading initial data:', err);
    } finally {
      setIsLoadingProfile(false);
    }
  };

  const fetchRecs = async (studentId: number = 1) => {
    setIsLoadingRecs(true);
    try {
      const res = await api.getRecommendations(studentId, 10);
      setRecommendations(res.recommendations);
    } catch (err) {
      console.error('Failed to load recommendations:', err);
    } finally {
      setIsLoadingRecs(false);
    }
  };

  useEffect(() => {
    fetchInitialData();
  }, []);

  const handleProfileUpdated = (updated: StudentProfile) => {
    setProfile(updated);
    fetchRecs(updated.id);
  };

  if (isLoadingProfile || !profile) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', background: '#f8fafc' }}>
        <Loader2 size={36} className="spin-icon" color="var(--primary)" style={{ marginBottom: '1rem' }} />
        <h3 style={{ fontWeight: 700, color: 'var(--text-primary)' }}>Loading Academia–Industry Collaboration Portal...</h3>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Initializing models and student database</p>
      </div>
    );
  }

  return (
    <div className="app-container">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} health={health} />
      <main className="main-content">
        {activeTab === 'profile' && (
          <ProfileEditor profile={profile} onProfileUpdated={handleProfileUpdated} />
        )}
        {activeTab === 'recommendations' && (
          <RecommendationList
            recommendations={recommendations}
            profile={profile}
            isLoading={isLoadingRecs}
            onRefresh={() => fetchRecs(profile.id)}
          />
        )}
        {activeTab === 'agent' && (
          <CareerAgentChat profile={profile} />
        )}
      </main>
    </div>
  );
};

export default App;
