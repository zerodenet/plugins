const number = new Intl.NumberFormat('zh-CN', { maximumFractionDigits: 2 });

export function artifactSizeLabel(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 ** 2) return `${number.format(bytes / 1024)} KiB`;
  if (bytes < 1024 ** 3) return `${number.format(bytes / 1024 ** 2)} MiB`;
  return `${number.format(bytes / 1024 ** 3)} GiB`;
}

export function hostVersionLabel(version) {
  const minimum = `≥ ${version.min}`;
  return version.max_exclusive ? `${minimum} 且 < ${version.max_exclusive}` : minimum;
}
