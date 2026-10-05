// At the top of your file, outside the component, or in a utility file
export const formatNumberForDisplay = (value) => {
  if (typeof value === 'number') {
    return new Intl.NumberFormat('it-IT').format(value);
  }
  return value; // Return as-is if not a number
};