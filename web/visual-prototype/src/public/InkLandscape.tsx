/** Original vector landscape, drawn for this prototype; no external art or fonts. */
export function InkLandscape() {
  return (
    <svg
      className="ink-landscape"
      viewBox="0 0 700 410"
      fill="none"
      aria-hidden="true"
    >
      <defs>
        <linearGradient
          id="ink-fade"
          x1="350"
          y1="80"
          x2="350"
          y2="400"
          gradientUnits="userSpaceOnUse"
        >
          <stop stopColor="#346157" stopOpacity=".3" />
          <stop offset="1" stopColor="#346157" stopOpacity="0" />
        </linearGradient>
        <filter id="ink-soft">
          <feGaussianBlur stdDeviation="2.3" />
        </filter>
      </defs>
      <circle
        cx="440"
        cy="123"
        r="58"
        stroke="#ad8d56"
        strokeOpacity=".26"
        strokeWidth=".8"
      />
      <path
        d="M90 325 137 280 161 278 198 195 231 231 255 138 285 170 310 253 339 207 363 230 389 120 408 89 432 182 454 161 479 250 511 200 533 243 557 227 614 323Z"
        fill="url(#ink-fade)"
        filter="url(#ink-soft)"
      />
      <path
        d="m140 312 56-63 17 21 33-38 32 54 39-82 21 38 35-36 30 53 28-31 34 57 41-39 56 68"
        stroke="#41675c"
        strokeOpacity=".2"
        strokeWidth="1.8"
      />
      <path
        d="m252 144 12 36-7 25 28 37m113-128-8 56 20 40-7 29"
        stroke="#305a50"
        strokeOpacity=".18"
      />
      <path
        d="M58 329c163-27 192 15 360-5 111-13 156-2 221 5M124 349c137-18 198 9 347-6M286 367h179M180 384h94"
        stroke="#658076"
        strokeOpacity=".23"
      />
      <path
        d="m100 307 3-39m-3 15-11-8m13 15 13-8m-10 26 12-45m-5 19 9-6"
        stroke="#31594b"
        strokeOpacity=".44"
        strokeWidth="1.6"
      />
      <path
        d="m510 69 7-3 7 3m-60-15 5-2 5 2m80 24 4-2 4 2"
        stroke="#294b40"
        strokeOpacity=".45"
      />
      <circle cx="366" cy="318" r="2" fill="#315b4f" fillOpacity=".4" />
      <path d="m363 321-6 4h20" stroke="#315b4f" strokeOpacity=".4" />
    </svg>
  );
}
