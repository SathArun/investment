import '@testing-library/jest-dom'

// Radix UI requires scrollIntoView + pointer capture APIs that jsdom doesn't implement
window.HTMLElement.prototype.scrollIntoView = () => {}
window.HTMLElement.prototype.hasPointerCapture = () => false
window.HTMLElement.prototype.releasePointerCapture = () => {}
