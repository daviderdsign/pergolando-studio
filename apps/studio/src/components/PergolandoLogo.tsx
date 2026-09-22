/**
 * The real Pergolando wordmark (D:\Lavori\App\logo_pergolando.svg), inlined
 * so its <text> renders with this app's own self-hosted Metropolis
 * @font-face instead of depending on the font being installed on the
 * visitor's machine (which it won't be, outside Davide's own PC). `fill`/
 * `stroke` are set to currentColor (patched from the source file's hardcoded
 * black) so the same asset works on both the light header and the dark
 * footer — just set `color` via CSS on the wrapper.
 */
const LOGO_SVG = `<svg viewBox="0 0 228 23" xmlns="http://www.w3.org/2000/svg" style="fill-rule:evenodd;clip-rule:evenodd;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:1.5;">
  <g transform="matrix(1,0,0,1,-89.396812,-166.619123)">
    <g transform="matrix(1,0,0,1,62.444932,129.500001)">
      <text x="24.776px" y="59.487px" fill="currentColor" style="font-family:'Metropolis-Bold','Metropolis';font-weight:700;font-size:32px;">PERGOLANDO</text>
    </g>
    <g transform="matrix(1,0,0,1,-0,1)">
      <path d="M193.409,170.614L181.909,184.114" style="fill:none;stroke:currentColor;stroke-width:4px;"/>
    </g>
    <g transform="matrix(1,0,0,1,118,1)">
      <path d="M193.409,170.614L181.909,184.114" style="fill:none;stroke:currentColor;stroke-width:4px;"/>
    </g>
  </g>
</svg>`;

export function PergolandoLogo({ className }: { className?: string }) {
  return <span className={className} dangerouslySetInnerHTML={{ __html: LOGO_SVG }} />;
}
