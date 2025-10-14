/**
 * Theme Hook
 */

import { useSelector } from 'react-redux';
import { RootState } from '../store';
import { Theme } from '../store/slices/themeSlice';

export const useTheme = () => {
  const theme = useSelector((state: RootState) => state.theme.currentTheme);
  return theme;
};
