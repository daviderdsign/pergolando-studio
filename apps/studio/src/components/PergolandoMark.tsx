/**
 * The "qb" brand mark (D:\Lavori\App\logo_qb.svg), inlined with
 * stroke:currentColor (patched from the source file's hardcoded #000) so the
 * same asset works on both the light header and the dark footer.
 */
const MARK_SVG = `<svg viewBox="0 0 162 191" xmlns="http://www.w3.org/2000/svg" style="fill-rule:evenodd;clip-rule:evenodd;stroke-miterlimit:10;">
  <path d="M77.823,172.528l0,-76.986c0,-16.934 -13.585,-30.976 -30.519,-31.002c-18.08,-0.028 -32.561,15.703 -30.326,34.221c1.853,15.35 14.78,26.701 30.242,26.674c2.094,-0.003 4.116,-0.224 6.084,-0.632c0.532,-0.11 1.028,0.307 1.028,0.851l0,46.8c0,0.49 0.397,0.887 0.887,0.887l21.789,0c0.449,0 0.814,-0.364 0.814,-0.814Z" style="fill:none;fill-rule:nonzero;stroke:currentColor;stroke-width:3.33px;"/>
  <path d="M50.027,94.987c0,-1.512 -1.228,-2.74 -2.74,-2.74c-1.512,0 -2.74,1.228 -2.74,2.74c0,1.512 1.228,2.74 2.74,2.74c1.512,0 2.74,-1.228 2.74,-2.74Z" style="fill:none;stroke:currentColor;stroke-width:3.33px;"/>
  <path d="M83.211,17.564l0,76.986c0,16.934 13.585,30.976 30.519,31.002c18.08,0.028 32.561,-15.703 30.326,-34.221c-1.853,-15.35 -14.78,-26.701 -30.242,-26.674c-2.094,0.003 -4.116,0.224 -6.084,0.632c-0.532,0.11 -1.028,-0.307 -1.028,-0.851l0,-46.8c0,-0.49 -0.397,-0.887 -0.887,-0.887l-21.789,0c-0.449,0 -0.814,0.364 -0.814,0.814Z" style="fill:none;fill-rule:nonzero;stroke:currentColor;stroke-width:3.33px;"/>
  <path d="M111.007,95.045c0,1.512 1.228,2.74 2.74,2.74c1.512,0 2.74,-1.228 2.74,-2.74c0,-1.512 -1.228,-2.74 -2.74,-2.74c-1.512,0 -2.74,1.228 -2.74,2.74Z" style="fill:none;stroke:currentColor;stroke-width:3.33px;"/>
</svg>`;

export function PergolandoMark({ className }: { className?: string }) {
  return <span className={className} dangerouslySetInnerHTML={{ __html: MARK_SVG }} />;
}
