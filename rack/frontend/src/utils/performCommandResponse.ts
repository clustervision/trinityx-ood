/**
 * Perform / rack_power JSON often uses `status` for power on/off (true=on, false=off),
 * not whether the command succeeded. Detect real failures from the message text.
 */
export function isPerformCommandFailureMessage(message: string): boolean {
  const m = message.trim().toLowerCase();
  if (!m) return false;
  return (
    m.includes('command execution failed') ||
    m.includes('exit code')
  );
}
