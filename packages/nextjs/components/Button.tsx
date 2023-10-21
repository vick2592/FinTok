// components/Button.tsx
import { ReactNode } from "react";
import Link from "next/link";

interface ButtonProps {
  href: string;
  children: ReactNode;
  className?: string;
}

const Button: React.FC<ButtonProps> = ({ href, children }) => {
  return (
    <Link href={href} passHref>
      {children}
    </Link>
  );
};

export default Button;
