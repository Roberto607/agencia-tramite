import {
  ArrowRight,
  Check,
  Facebook,
  Headset,
  Instagram,
  LaptopMinimal,
  Mail,
  MessageCircle,
  MapPin,
  PhoneCall,
  Linkedin,
  ShieldCheck,
  Zap,
  Youtube,
} from 'lucide-react'
import ApplicationPage from './ApplicationPage'


const benefits = [
  {
    title: 'Proceso rápido',
    description: 'Completa tus trámites en menos tiempo.',
    Icon: Zap,
  },
  {
    title: 'Seguro y confiable',
    description: 'Tus datos siempre protegidos.',
    Icon: ShieldCheck,
  },
  {
    title: '100% en línea',
    description: 'Desde cualquier lugar.',
    Icon: LaptopMinimal,
  },
  {
    title: 'Soporte especializado',
    description: 'Estamos para ayudarte.',
    Icon: Headset,
  },
]


function Hero() {
  return (
    <section className="hero" id="inicio" aria-labelledby="hero-title">
      <div className="hero__image" aria-hidden="true" />
      <div className="hero__content">
        <div className="hero__copy">
          <div className="hero__badge">
            <span className="hero__badge-icon"><Check size={16} strokeWidth={3} /></span>
            Tu gestión, más fácil y rápido
          </div>
          <h1 id="hero-title">LB&amp;A Consulter<br /><span>Agencia de trámites y consultoría</span></h1>
          <p>
            Te acompañamos en tus gestiones personales y empresariales con orientación cercana y un proceso sencillo.
            Realiza tu solicitud en línea, desde donde estés.
          </p>
          <div className="hero__highlights">
            <span>Atención personalizada</span>
            <span>Trámites en línea</span>
            <span>Seguimiento de tu consulta</span>
          </div>
          <a className="primary-button hero__action" href="/#/solicitud">
            Regístrate o inicia sesión <ArrowRight size={18} aria-hidden="true" />
          </a>
          <span className="hero__note">Crea tu cuenta para iniciar y consultar tu solicitud.</span>
        </div>
      </div>
    </section>
  )
}

function Benefits() {
  return (
    <section className="benefits" id="servicios" aria-label="Beneficios">
      <div className="benefits-inner">
        {benefits.map(({ title, description, Icon }) => (
          <article className="benefit" key={title}>
            <div className="benefit__icon"><Icon size={34} strokeWidth={2.4} aria-hidden="true" /></div>
            <div className="benefit__copy">
              <h2>{title}</h2>
              <p>{description}</p>
            </div>
          </article>
        ))}
      </div>
    </section>
  )
}

function PhoneContact() {
  return (
    <section className="phone-contact" aria-labelledby="phone-contact-title">
      <div className="phone-contact__inner">
        <div className="phone-contact__icon"><PhoneCall size={25} aria-hidden="true" /></div>
        <div className="phone-contact__copy">
          <h2 id="phone-contact-title">¿Necesitas ayuda con tu trámite?</h2>
          <p>Comunícate con nuestro equipo de atención.</p>
        </div>
        <a className="phone-contact__link" href="https://wa.me/5358049659" target="_blank" rel="noreferrer">
          <MessageCircle size={17} aria-hidden="true" /> WhatsApp: +53 58049659
        </a>
      </div>
    </section>
  )
}

function Footer() {
  return (
    <footer className="site-footer" id="contacto">
      <div className="footer-main">
        <div className="footer-intro">
          <span className="footer-intro__eyebrow">LB&amp;A Consulter</span>
          <h2>Agencia de trámites<br />y consultoría</h2>
          <p>Atención y acompañamiento para tus gestiones.</p>
        </div>
        <div className="footer-contact">
          <h2>Contacto</h2>
          <a href="https://wa.me/5358049659" target="_blank" rel="noreferrer"><MessageCircle size={17} aria-hidden="true" /> +53 58049659</a>
          <a href="mailto:lbaconsulter@gmail.com"><Mail size={17} fill="currentColor" aria-hidden="true" /> lbaconsulter@gmail.com</a>
          <p><MapPin size={18} fill="currentColor" aria-hidden="true" /> Cra. 123 #45-67, Ciudad</p>
        </div>
        <div className="footer-social">
          <h2>Síguenos</h2>
          <div className="social-links">
            <a href="https://www.facebook.com/" aria-label="Facebook" title="Facebook"><Facebook size={18} aria-hidden="true" /></a>
            <a href="https://www.instagram.com/" aria-label="Instagram" title="Instagram"><Instagram size={18} aria-hidden="true" /></a>
            <a href="https://www.youtube.com/" aria-label="YouTube" title="YouTube"><Youtube size={18} aria-hidden="true" /></a>
            <a href="https://www.linkedin.com/" aria-label="LinkedIn" title="LinkedIn"><Linkedin size={18} aria-hidden="true" /></a>
          </div>
        </div>
      </div>
      <div className="footer-bottom">
        <span>© {new Date().getFullYear()} LB&amp;A Consulter. Todos los derechos reservados.</span>
        <span>Agencia de trámites y consultoría</span>
      </div>
    </footer>
  )
}

export default function App() {
  if (window.location.hash === '#/solicitud') {
    return <ApplicationPage />
  }

  return (
    <>
      <main>
        <Hero />
        <Benefits />
        <PhoneContact />
        <section className="anchor-target" id="preguntas" aria-label="Preguntas frecuentes" />
      </main>
      <Footer />
    </>
  )
}
