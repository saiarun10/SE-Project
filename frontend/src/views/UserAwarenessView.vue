<template>
    <Navbar />
  <div class="awareness-container">
    <!-- Main Content -->
    <div class="newsletter-card">
      <header class="newsletter-header">
        <div class="newsletter-meta">
          <span>{{ currentArticle.source }}</span>
          <span>{{ currentArticle.date }}</span>
        </div>
        <h1 class="newsletter-title">{{ currentArticle.title }}</h1>
      </header>
      
      <div class="newsletter-body">
        <h2 class="section-title">{{ currentArticle.sectionTitle }}</h2>
        
        <div class="content-text" v-html="currentArticle.content"></div>
        
        <div class="highlight-box" v-if="currentArticle.keyInsight">
          <strong>Key Insight:</strong> {{ currentArticle.keyInsight }}
        </div>
      </div>
      
      <div class="navigation-buttons">
        <button 
          class="nav-btn" 
          @click="previousArticle" 
          :disabled="currentIndex === 0"
        >
          ← Previous
        </button>
        
        <div class="article-counter">
          {{ currentIndex + 1 }} / {{ awarenessArticles.length }}
        </div>
        
        <button 
          class="nav-btn" 
          @click="nextArticle" 
          :disabled="currentIndex === awarenessArticles.length - 1"
        >
          Next →
        </button>
      </div>
    </div>
  </div>
  <AppFooter />
</template>

<script>
import Navbar from '@/components/Navbar.vue'
import AppFooter from '@/components/Footer.vue'
import App from '../App.vue';

export default {
  name: 'Awareness',
   components: {
    Navbar,
    AppFooter
   },
  data() {
    return {
      currentIndex: 0,
      awarenessArticles: [
        {
          source: 'Trading Insights',
      
          title: 'Be Aware of Tempting Returns',
          sectionTitle: 'Facts and Stories',
          content: `
            <p>A new study conducted by the Securities and Exchange Board of India (SEBI) has revealed that over 9 out of 10 individual traders in the equity futures and options (F&O) segment continue to incur significant losses.</p>
            <p>The aggregate losses of individual traders exceeded <strong>1.8 lakh crores</strong> over the three-year period between FY22 and FY24.</p>
            <p>This staggering figure highlights the challenging nature of F&O trading and the importance of understanding market dynamics before investing.</p>
          `,
          keyInsight: 'Over 90% of F&O traders lose money consistently. Think twice before entering derivatives trading.'
        },
        {
          source: 'Trading Insights',
   
          title: 'The Psychology of Trading Losses',
          sectionTitle: 'Behavioral Finance',
          content: `
            <p>Most traders fall victim to <strong>overconfidence bias</strong> and believe they can beat the market consistently.</p>
            <p>Research shows that frequent trading leads to poor returns due to transaction costs and emotional decision-making.</p>
            <p>The average retail trader underperforms market indices by 3-7% annually due to poor timing and excessive trading.</p>
          `,
          keyInsight: 'Emotional trading is the enemy of wealth creation. Discipline and patience are your best allies.'
        },
        {
          source: 'Trading Insights',
    
          title: 'Hidden Costs of Active Trading',
          sectionTitle: 'Cost Analysis',
          content: `
            <p>Beyond the obvious brokerage fees, active trading involves multiple hidden costs:</p>
            <ul>
              <li><strong>Bid-ask spreads</strong> that eat into profits</li>
              <li><strong>Slippage</strong> during volatile market conditions</li>
              <li><strong>Opportunity cost</strong> of time spent analyzing markets</li>
              <li><strong>Tax implications</strong> on short-term gains</li>
            </ul>
            <p>These costs compound over time and significantly impact returns.</p>
          `,
          keyInsight: 'The house always wins. Transaction costs and taxes make frequent trading a losing proposition.'
        },
        {
          source: 'Trading Insights',
       
          title: 'The Allure of Quick Money',
          sectionTitle: 'Reality Check',
          content: `
            <p>Social media and advertisements often showcase success stories of traders making quick profits, but they rarely mention the failures.</p>
            <p><strong>Survivorship bias</strong> makes it seem like trading is easier than it actually is.</p>
            <p>For every success story shared, there are hundreds of traders who lost their savings but remain silent about their losses.</p>
            <p>Building wealth through investments requires time, patience, and consistent contributions - not gambling on daily price movements.</p>
          `,
          keyInsight: 'Get-rich-quick schemes often lead to get-poor-quick results. Sustainable wealth building takes time.'
        },
        {
          source: 'Trading Insights',
       
          title: 'Smart Alternatives to Day Trading',
          sectionTitle: 'Better Strategies',
          content: `
            <p>Instead of day trading, consider these proven wealth-building strategies:</p>
            <ul>
              <li><strong>SIP in Mutual Funds</strong> - Systematic and disciplined investing</li>
              <li><strong>Index Fund Investing</strong> - Low-cost, diversified exposure</li>
              <li><strong>Blue-chip Stock Investing</strong> - Quality companies for long-term growth</li>
              <li><strong>Emergency Fund</strong> - Financial security before taking risks</li>
            </ul>
            <p>These strategies have created more millionaires than day trading ever will.</p>
          `,
          keyInsight: 'Time in the market beats timing the market. Consistent investing is the key to wealth creation.'
        }
      ]
    }
  },
  computed: {
    currentArticle() {
      return this.awarenessArticles[this.currentIndex];
    }
  },
  methods: {
    nextArticle() {
      if (this.currentIndex < this.awarenessArticles.length - 1) {
        this.currentIndex++;
      }
    },
    previousArticle() {
      if (this.currentIndex > 0) {
        this.currentIndex--;
      }
    }
  }
}
</script>

<style scoped>
.awareness-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 20px;
}

.newsletter-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
  overflow: hidden;
  max-width: 800px;
  margin: 0 auto;
  transition: transform 0.3s ease;
}

.newsletter-card:hover {
  transform: translateY(-2px);
}

.newsletter-header {
  padding: 2rem;
  border-bottom: 1px solid #e9ecef;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}

.newsletter-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  font-size: 0.9rem;
  color: #666;
}

.newsletter-title {
  font-size: 2rem;
  font-weight: bold;
  color: #333;
  margin-bottom: 0.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.newsletter-body {
  padding: 2rem;
}

.section-title {
  font-size: 1.3rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
  color: #333;
  border-left: 4px solid #667eea;
  padding-left: 1rem;
}

.content-text {
  font-size: 1rem;
  line-height: 1.7;
  color: #555;
  margin-bottom: 2rem;
}

.content-text p {
  margin-bottom: 1rem;
}

.content-text ul {
  margin: 1rem 0;
  padding-left: 1.5rem;
}

.content-text li {
  margin-bottom: 0.5rem;
}

.highlight-box {
  background: linear-gradient(120deg, #a8edea 0%, #fed6e3 100%);
  padding: 1rem;
  border-radius: 8px;
  border-left: 4px solid #667eea;
  margin: 1.5rem 0;
}

.navigation-buttons {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  background: #f8f9fa;
  border-top: 1px solid #e9ecef;
}

.nav-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 25px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.3s ease;
  min-width: 100px;
}

.nav-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.nav-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.article-counter {
  font-size: 0.9rem;
  color: #666;
  font-weight: 500;
  background: white;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  border: 1px solid #e9ecef;
}

/* Responsive Design */
@media (max-width: 768px) {
  .awareness-container {
    padding: 1rem 10px;
  }

  .newsletter-title {
    font-size: 1.5rem;
  }

  .newsletter-header,
  .newsletter-body {
    padding: 1.5rem;
  }

  .navigation-buttons {
    padding: 1rem 1.5rem;
    flex-direction: column;
    gap: 1rem;
  }

  .nav-btn {
    width: 100%;
  }

  .article-counter {
    order: -1;
  }
}

/* Animation for content changes */
.newsletter-body {
  animation: fadeIn 0.5s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>