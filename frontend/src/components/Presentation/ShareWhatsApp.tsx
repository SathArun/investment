interface Props {
  pdfUrl: string
}

export function ShareWhatsApp({ pdfUrl }: Props) {
  const shareUrl = `https://wa.me/?text=${encodeURIComponent(`Check out this investment comparison: ${pdfUrl}`)}`

  return (
    <a
      href={shareUrl}
      target="_blank"
      rel="noopener noreferrer"
      className="inline-flex items-center gap-2 bg-green-500 text-white px-4 py-2 rounded-md hover:bg-green-600 transition-colors"
    >
      Share via WhatsApp
    </a>
  )
}
