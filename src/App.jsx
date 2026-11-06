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
  UserRound,
  Globe2,
  ClipboardCheck,
} from 'lucide-react'
import { useEffect, useState } from 'react'
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

const serviceHighlights = [
  {
    title: 'Atención personalizada',
    description: 'Te orientamos según tu caso y resolvemos tus dudas durante el proceso.',
    Icon: UserRound,
  },
  {
    title: 'Trámites en línea',
    description: 'Envía tu solicitud y los documentos necesarios desde donde estés.',
    Icon: Globe2,
  },
  {
    title: 'Seguimiento de tu consulta',
    description: 'Nuestro equipo analiza tu solicitud y te mantiene al tanto.',
    Icon: ClipboardCheck,
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
          <a className="primary-button hero__action" href="/#/solicitud">
            Regístrate o inicia sesión <ArrowRight size={18} aria-hidden="true" />
          </a>
          <span className="hero__note">Crea tu cuenta para iniciar y consultar tu solicitud.</span>
        </div>
      </div>
    </section>
  )
}

function ServiceHighlights() {
  return (
    <section className="service-highlights" aria-labelledby="service-highlights-title">
      <div className="service-highlights__inner">
        <div className="service-highlights__intro">
          <span className="service-highlights__eyebrow">Estamos contigo</span>
          <h2 id="service-highlights-title">Tus gestiones, con acompañamiento de principio a fin</h2>
          <p>
            Te acompañamos en tus gestiones personales y empresariales con orientación cercana y un proceso sencillo.
            Realiza tu solicitud en línea, desde donde estés.
          </p>
        </div>
        <div className="service-highlights__grid">
          {serviceHighlights.map(({ title, description, Icon }, index) => (
            <article className="service-highlight-card" key={title}>
              <span className="service-highlight-card__number">0{index + 1}</span>
              <div className="service-highlight-card__icon">
                <Icon size={25} strokeWidth={2.2} aria-hidden="true" />
              </div>
              <h3>{title}</h3>
              <p>{description}</p>
            </article>
          ))}
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
          <div className="footer-intro__brand">
            <img src="/logo-lba.png" alt="Logo de LB&A Consulter" />
            <div>
              <span className="footer-intro__eyebrow">LB&amp;A Consulter</span>
              <h2>Agencia de trámites<br />y consultoría</h2>
            </div>
          </div>
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
  const [isApplicationPage, setIsApplicationPage] = useState(
    () => window.location.hash === '#/solicitud',
  )

  useEffect(() => {
    function syncRoute() {
      setIsApplicationPage(window.location.hash === '#/solicitud')
    }

    window.addEventListener('hashchange', syncRoute)
    return () => window.removeEventListener('hashchange', syncRoute)
  }, [])

  if (isApplicationPage) {
    return <ApplicationPage />
  }

  return (
    <>
      <main>
        <Hero />
        <ServiceHighlights />
        <Benefits />
        <PhoneContact />
        <section className="anchor-target" id="preguntas" aria-label="Preguntas frecuentes" />
      </main>
      <Footer />
    </>
  )
}
