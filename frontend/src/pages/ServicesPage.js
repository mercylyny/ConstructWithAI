import React from 'react';

function ServicesPage() {
  const services = [
    {
      title: 'AI Blueprint Analysis',
      desc: 'Instantly extract walls, measurements, and layouts from construction PDFs using advanced OCR.',
      icon: '📐'
    },
    {
      title: 'Automated BOQ Generation',
      desc: 'Generate comprehensive Bills of Quantities for masonry, steel, and concrete in seconds.',
      icon: '📊'
    },
    {
      title: 'Hybrid Estimation',
      desc: 'Combine AI-detected dimensions with manual engineer overrides for perfect accuracy.',
      icon: '🏗️'
    },
    {
      title: '3D BIM Export',
      desc: 'Export your 2D plans into rich 3D IFC models ready for standard BIM software.',
      icon: '🏙️'
    }
  ];

  return (
    <div className="fade-in page-container">
      <div style={{ textAlign: 'center', marginBottom: '4rem' }}>
        <h2>Our Platform Services</h2>
        <p style={{ color: 'var(--text-secondary)', maxWidth: '600px', margin: '0 auto' }}>
          Leverage our suite of AI-powered tools to accelerate your construction estimation workflows by up to 10x while maintaining complete control.
        </p>
      </div>

      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', 
        gap: '2rem' 
      }}>
        {services.map((service, index) => (
          <div key={index} className="glass-panel" style={{ 
            padding: '2rem',
            transition: 'transform 0.3s ease',
            cursor: 'pointer'
          }} 
          onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-5px)'}
          onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}
          >
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>{service.icon}</div>
            <h3 style={{ fontSize: '1.25rem', marginBottom: '1rem' }}>{service.title}</h3>
            <p style={{ color: 'var(--text-secondary)', lineHeight: '1.6' }}>{service.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default ServicesPage;
