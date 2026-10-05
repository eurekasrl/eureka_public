// src/components/SelectionGrid.jsx
import React from 'react';
import { Typography, Box, Grid, Paper } from '@mui/material';

/**
 * A reusable component for rendering a grid of selectable items.
 *
 * @param {object} props - The component props.
 * @param {Array<object>} props.data - The array of items to display. Each item should have an 'id' property.
 * @param {string | number | null} props.selectedId - The ID of the currently selected item.
 * @param {(id: string | number) => void} props.onSelect - The function to call when an item is selected.
 * @param {string} props.title - The title for the selection section.
 * @param {(item: object) => React.ReactNode} props.renderItemContent - A function that returns the JSX to render inside each Paper component.
 */
const SelectionGrid = ({ data, selectedId, onSelect, title, renderItemContent }) => {
    return (
        <Box sx={{ mt: 6 }}>
            <Typography variant="h4" component="h1" gutterBottom>
                {title}
            </Typography>
            <Grid container spacing={3} justifyContent="center" sx={{ mt: 3 }}>
                {data.length === 0 ? (
                    <Typography color="text.secondary">Nessun {title.toLowerCase().split(' ').slice(2).join(' ')} trovato.</Typography>
                ) : (
                    data.map((item) => (
                        <Grid
                            key={item.id}
                            // Using the new Grid v2 syntax for responsive column spanning
                            sx={{
                                gridColumn: { xs: 'span 12', sm: 'span 6', md: 'span 4' }
                            }}
                        >
                            <Paper
                                // Add role="button" and tabIndex for accessibility
                                role="button"
                                tabIndex={0}
                                elevation={selectedId === item.id ? 8 : 3}
                                sx={{
                                    p: 3,
                                    height: '100%',
                                    display: 'flex',
                                    flexDirection: 'column',
                                    justifyContent: 'space-between',
                                    alignItems: 'center',
                                    textAlign: 'center',
                                    cursor: 'pointer',
                                    transition: 'transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out, background-color 0.2s ease-in-out',
                                    '&:hover': {
                                        transform: 'translateY(-5px)',
                                        boxShadow: '0 6px 12px rgba(0,0,0,0.15)',
                                    },
                                    // Focus style for keyboard navigation
                                    '&:focus': {
                                        outline: '2px solid #00bcd4', // Highlight on focus
                                        outlineOffset: '2px',
                                    },
                                    backgroundColor: selectedId === item.id ? '#e0f7fa' : 'inherit',
                                    border: selectedId === item.id ? '2px solid #00bcd4' : '2px solid transparent',
                                }}
                                onClick={() => onSelect(item.id)}
                                // Handle keyboard navigation for accessibility
                                onKeyDown={(event) => {
                                    if (event.key === 'Enter' || event.key === ' ') {
                                        event.preventDefault(); // Prevent default scroll for space bar
                                        onSelect(item.id);
                                    }
                                }}
                            >
                                {renderItemContent(item)}
                            </Paper>
                        </Grid>
                    ))
                )}
            </Grid>
        </Box>
    );
};

export default SelectionGrid;