import React from 'react';

const Logo = ({ className = 'w-10 h-10' }) => {
  return (
    <img 
      src="https://customer-assets.emergentagent.com/job_bigbean-system/artifacts/cg0dat1r_BBC-Logo.png" 
      alt="BigBean Cafe" 
      className={className}
    />
  );
};

export default Logo;