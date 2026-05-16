import { motion } from 'motion/react';
import { Entity } from '../data/entities';

interface WheelSelectorProps {
  items: Entity[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  align: 'left' | 'right';
}

export function WheelSelector({ items, selectedId, onSelect, align }: WheelSelectorProps) {
  const selectedIndex = items.findIndex(item => item.id === selectedId);

  const handleWheel = (e: React.WheelEvent) => {
    // Only handle significant scrolls to avoid jitter
    if (Math.abs(e.deltaY) < 15) return;
    
    // Determine direction
    const direction = e.deltaY > 0 ? 1 : -1;
    const nextIndex = selectedIndex + direction;
    
    if (nextIndex >= 0 && nextIndex < items.length) {
      onSelect(items[nextIndex].id);
    }
  };

  return (
    <div 
      onWheel={handleWheel}
      className="relative h-[500px] w-56 flex items-center justify-center overflow-visible select-none"
    >
      <div className="relative w-full h-full">
        {items.map((item, index) => {
          // If nothing is selected, behave as if 0 is selected to show list properly
          const activeIdx = selectedIndex !== -1 ? selectedIndex : Math.floor(items.length / 2);
          const distance = index - activeIdx;
          const absDistance = Math.abs(distance);
          const isActive = selectedId === item.id;

          // Limit render to items near active (5 nodes above, 5 nodes below)
          if (absDistance > 5) return null;

          // Wheel layout math
          // Vertical shift
          const translateY = distance * 64; 
          // Outward curving. Left side curves left (-x) as distance grows. Right side curves right (+x).
          const curveCurve = Math.pow(absDistance, 1.5) * 8;
          const translateX = align === 'left' ? -curveCurve : curveCurve;
          
          // Scaling and styling
          const scale = 1 - (absDistance * 0.06);
          const opacity = isActive ? 1 : Math.max(0, 0.5 - (absDistance * 0.15));

          return (
            <motion.div
              key={item.id}
              onClick={() => onSelect(item.id)}
              className={`absolute w-full cursor-pointer flex flex-col justify-center ${align === 'left' ? 'items-end pr-4 text-right' : 'items-start pl-4 text-left'}`}
              style={{
                top: '50%',
                marginTop: '-32px', // half height
                height: '64px',
                transformOrigin: align === 'left' ? 'right center' : 'left center'
              }}
              animate={{
                y: translateY,
                x: translateX,
                scale,
                opacity,
              }}
              transition={{ type: 'spring', stiffness: 350, damping: 30 }}
            >
              <div
                className={`whitespace-nowrap transition-colors duration-300 ${
                  isActive 
                    ? 'text-[24px] font-bold text-zinc-900 tracking-tight' 
                    : 'text-[18px] font-medium text-zinc-300 hover:text-zinc-500'
                }`}
              >
                {item.name}
              </div>
            </motion.div>
          )
        })}
      </div>
    </div>
  );
}
