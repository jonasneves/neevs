// Translation data
const translations = {
  en: {
    // Layout/Navigation
    'nav.howItWorks': 'How It Works',
    'footer.powered': 'Powered by GitHub Actions + AI • All pipelines run serverless • Only pay for AI API usage',

    // Home Page
    'home.title': 'Neevs',
    'home.subtitle': 'Automated insights from AI-powered channels · Subscribe to what matters',
    'home.badge.fresh': 'Always Fresh',
    'home.badge.automated': 'Fully Automated',
    'home.badge.ai': 'AI-Powered',
    'home.subdescription': 'Free to read · Subscribe to channels you love · Built with AgentFlow',
    'home.section.title': 'Browse All Channels',
    'home.pipeline.status.active': 'active',
    'home.pipeline.status.planned': 'planned',
    'home.pipeline.schedule': 'Schedule:',
    'home.pipeline.plannedSchedule': 'Planned Schedule:',
    'home.pipeline.dataSource': 'Data Source:',
    'home.pipeline.aiTask': 'AI Task:',
    'home.pipeline.noArtifacts': 'No artifacts generated yet • Pipeline coming soon',

    // Pipeline Names
    'pipeline.news.name': 'AI News Bias Detector',
    'pipeline.news.description': 'Compare how ChatGPT, Llama, and other AI models interpret the same story differently - expose AI bias and think critically',
    'pipeline.news.schedule': 'Every 6 hours',
    'pipeline.news.source': 'Google News',
    'pipeline.news.task': 'Multi-AI comparison, bias detection, sentiment analysis',

    'pipeline.academic.name': 'Academic Research Pipeline',
    'pipeline.academic.description': 'Weekly digest of trending research papers with social buzz tracking',
    'pipeline.academic.schedule': 'Weekly (Sundays)',
    'pipeline.academic.source': 'arXiv API, Twitter/X, Reddit',
    'pipeline.academic.task': 'Paper summarization, trend analysis',

    'pipeline.market.name': 'Market Analysis Pipeline',
    'pipeline.market.description': 'Real-time crypto and stock market analysis with AI insights',
    'pipeline.market.schedule': 'Daily (6 AM EST)',
    'pipeline.market.source': 'CoinGecko, Yahoo Finance, News APIs',
    'pipeline.market.task': 'Sentiment analysis, trend prediction',

    // Perspectives Page
    'perspectives.title': 'AI News Bias Detector',
    'perspectives.subtitle': 'Compare how different AI models interpret the same news stories',
    'perspectives.description': 'See the same story through multiple AI perspectives. Compare ChatGPT, Llama, Phi, and more to understand how AI bias shapes information.',
    'perspectives.loading': 'Loading AI perspectives...',
    'perspectives.noData': 'No perspectives available yet. Check back later!',
    'perspectives.backToHome': '← Back to Home',
    'perspectives.article': 'Article',
    'perspectives.source': 'Source:',
    'perspectives.published': 'Published:',
    'perspectives.viewOriginal': 'View Original Article →',
    'perspectives.aiPerspectives': 'AI Perspectives',
    'perspectives.model': 'Model',
    'perspectives.sentiment': 'Sentiment',
    'perspectives.summary': 'Summary',
    'perspectives.keyPoints': 'Key Points',
    'perspectives.tone': 'Tone',
    'perspectives.biasIndicators': 'Bias Indicators',
    'perspectives.readArticle': 'Read Full Article',
    'perspectives.cta.title': 'Get AI Perspectives Delivered',
    'perspectives.cta.description': 'Subscribe to receive daily AI news analysis comparing multiple perspectives',
    'perspectives.cta.button': 'Subscribe via Email',

    // How It Works Page
    'howItWorks.title': 'How AgentFlow Works',
    'howItWorks.subtitle': 'Build AI-powered channels that run automatically, for free',
    'howItWorks.architecture.title': 'Architecture Overview',
    'howItWorks.architecture.description': 'AgentFlow uses GitHub Actions as the orchestration layer, eliminating the need for servers or complex infrastructure.',

    // Artifacts
    'artifact.researchRoundup': 'Weekly Research Roundup',
    'artifact.researchDescription': 'Engaging weekly digest of trending research papers with social buzz tracking and editorial analysis.',
    'artifact.marketPulse': 'Market Pulse',
    'artifact.marketDescription': 'Real-time crypto and stock market analysis with AI-powered insights',

    // Common
    'common.papers': 'papers',
    'common.posts': 'posts',
    'common.articles': 'articles',
    'common.assets': 'assets tracked',
    'common.aiModels': 'AI models',
    'common.lastUpdated': 'Last Updated',
  },

  'pt-BR': {
    // Layout/Navigation
    'nav.howItWorks': 'Como Funciona',
    'footer.powered': 'Desenvolvido com GitHub Actions + IA • Todos os pipelines são serverless • Pague apenas pelo uso da API de IA',

    // Home Page
    'home.title': 'Neevs',
    'home.subtitle': 'Insights automatizados de canais com IA · Assine o que importa',
    'home.badge.fresh': 'Sempre Atualizado',
    'home.badge.automated': 'Totalmente Automatizado',
    'home.badge.ai': 'Alimentado por IA',
    'home.subdescription': 'Gratuito para ler · Assine os canais que você ama · Construído com AgentFlow',
    'home.section.title': 'Navegue por Todos os Canais',
    'home.pipeline.status.active': 'ativo',
    'home.pipeline.status.planned': 'planejado',
    'home.pipeline.schedule': 'Agenda:',
    'home.pipeline.plannedSchedule': 'Agenda Planejada:',
    'home.pipeline.dataSource': 'Fonte de Dados:',
    'home.pipeline.aiTask': 'Tarefa de IA:',
    'home.pipeline.noArtifacts': 'Nenhum artefato gerado ainda • Pipeline em breve',

    // Pipeline Names
    'pipeline.news.name': 'Detector de Viés de Notícias de IA',
    'pipeline.news.description': 'Compare como ChatGPT, Llama e outros modelos de IA interpretam a mesma história de forma diferente - exponha o viés da IA e pense criticamente',
    'pipeline.news.schedule': 'A cada 6 horas',
    'pipeline.news.source': 'Google Notícias',
    'pipeline.news.task': 'Comparação multi-IA, detecção de viés, análise de sentimento',

    'pipeline.academic.name': 'Pipeline de Pesquisa Acadêmica',
    'pipeline.academic.description': 'Resumo semanal de artigos de pesquisa em alta com rastreamento de buzz social',
    'pipeline.academic.schedule': 'Semanal (Domingos)',
    'pipeline.academic.source': 'API arXiv, Twitter/X, Reddit',
    'pipeline.academic.task': 'Resumo de artigos, análise de tendências',

    'pipeline.market.name': 'Pipeline de Análise de Mercado',
    'pipeline.market.description': 'Análise de mercado cripto e de ações em tempo real com insights de IA',
    'pipeline.market.schedule': 'Diário (6h EST)',
    'pipeline.market.source': 'CoinGecko, Yahoo Finance, APIs de Notícias',
    'pipeline.market.task': 'Análise de sentimento, previsão de tendências',

    // Perspectives Page
    'perspectives.title': 'Detector de Viés de Notícias de IA',
    'perspectives.subtitle': 'Compare como diferentes modelos de IA interpretam as mesmas notícias',
    'perspectives.description': 'Veja a mesma história através de múltiplas perspectivas de IA. Compare ChatGPT, Llama, Phi e outros para entender como o viés da IA molda a informação.',
    'perspectives.loading': 'Carregando perspectivas de IA...',
    'perspectives.noData': 'Nenhuma perspectiva disponível ainda. Volte mais tarde!',
    'perspectives.backToHome': '← Voltar para Início',
    'perspectives.article': 'Artigo',
    'perspectives.source': 'Fonte:',
    'perspectives.published': 'Publicado:',
    'perspectives.viewOriginal': 'Ver Artigo Original →',
    'perspectives.aiPerspectives': 'Perspectivas de IA',
    'perspectives.model': 'Modelo',
    'perspectives.sentiment': 'Sentimento',
    'perspectives.summary': 'Resumo',
    'perspectives.keyPoints': 'Pontos-Chave',
    'perspectives.tone': 'Tom',
    'perspectives.biasIndicators': 'Indicadores de Viés',
    'perspectives.readArticle': 'Ler Artigo Completo',
    'perspectives.cta.title': 'Receba Perspectivas de IA',
    'perspectives.cta.description': 'Assine para receber análises diárias de notícias de IA comparando múltiplas perspectivas',
    'perspectives.cta.button': 'Assinar via Email',

    // How It Works Page
    'howItWorks.title': 'Como o AgentFlow Funciona',
    'howItWorks.subtitle': 'Construa canais alimentados por IA que executam automaticamente, gratuitamente',
    'howItWorks.architecture.title': 'Visão Geral da Arquitetura',
    'howItWorks.architecture.description': 'O AgentFlow usa o GitHub Actions como camada de orquestração, eliminando a necessidade de servidores ou infraestrutura complexa.',

    // Artifacts
    'artifact.researchRoundup': 'Resumo Semanal de Pesquisas',
    'artifact.researchDescription': 'Resumo semanal envolvente de artigos de pesquisa em alta com rastreamento de buzz social e análise editorial.',
    'artifact.marketPulse': 'Pulso do Mercado',
    'artifact.marketDescription': 'Análise de mercado cripto e de ações em tempo real com insights de IA',

    // Common
    'common.papers': 'artigos',
    'common.posts': 'posts',
    'common.articles': 'artigos',
    'common.assets': 'ativos rastreados',
    'common.aiModels': 'modelos de IA',
    'common.lastUpdated': 'Última Atualização',
  }
};

// Translation system
class I18n {
  constructor() {
    this.currentLanguage = localStorage.getItem('language') || 'en';
    this.init();
  }

  init() {
    // Apply translations on page load
    document.addEventListener('DOMContentLoaded', () => {
      this.applyTranslations();
      this.updateLanguageToggle();
    });
  }

  translate(key) {
    return translations[this.currentLanguage]?.[key] || translations.en[key] || key;
  }

  setLanguage(lang) {
    this.currentLanguage = lang;
    localStorage.setItem('language', lang);
    this.applyTranslations();
    this.updateLanguageToggle();

    // Update HTML lang attribute
    document.documentElement.lang = lang;
  }

  applyTranslations() {
    // Translate all elements with data-i18n attribute
    document.querySelectorAll('[data-i18n]').forEach(element => {
      const key = element.getAttribute('data-i18n');
      const translation = this.translate(key);

      // Update text content or placeholder based on element type
      if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
        element.placeholder = translation;
      } else {
        element.textContent = translation;
      }
    });

    // Translate elements with data-i18n-html (for HTML content)
    document.querySelectorAll('[data-i18n-html]').forEach(element => {
      const key = element.getAttribute('data-i18n-html');
      const translation = this.translate(key);
      element.innerHTML = translation;
    });
  }

  updateLanguageToggle() {
    const toggleBtn = document.getElementById('language-toggle');
    if (toggleBtn) {
      const flag = toggleBtn.querySelector('.flag');
      const langText = toggleBtn.querySelector('.lang-text');

      if (this.currentLanguage === 'en') {
        // Currently English - show US flag and option to switch to PT-BR on hover
        if (flag) flag.textContent = '🇺🇸';
        if (langText) langText.textContent = 'EN';
        toggleBtn.setAttribute('aria-label', 'Switch to Portuguese');
        toggleBtn.setAttribute('title', 'Mudar para Português');
      } else {
        // Currently Portuguese - show BR flag and option to switch to EN on hover
        if (flag) flag.textContent = '🇧🇷';
        if (langText) langText.textContent = 'PT';
        toggleBtn.setAttribute('aria-label', 'Mudar para Inglês');
        toggleBtn.setAttribute('title', 'Switch to English');
      }
    }
  }

  toggleLanguage() {
    const newLang = this.currentLanguage === 'en' ? 'pt-BR' : 'en';
    this.setLanguage(newLang);
  }
}

// Create global instance
window.i18n = new I18n();

// Toggle function for button
function toggleLanguage() {
  window.i18n.toggleLanguage();
}
