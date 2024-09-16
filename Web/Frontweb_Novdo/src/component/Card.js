// src/component/Card.js
import React from 'react';
import './Card.css';

const Card = ({ title, children, footer, className }) => {
  return (
    <div className={`card-container ${className}`}>
      {title && <div className="card-header">{title}</div>}
      <div className="card-content">
        {children}
      </div>
      {footer && <div className="card-footer">{footer}</div>}
    </div>
  );
};

export default Card;
