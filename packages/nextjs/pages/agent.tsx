import type { NextPage } from "next";
import { MetaHeader } from "~~/components/MetaHeader";

const Agent: NextPage = () => {
  return (
    <>
      <MetaHeader title="Trading Agent" description="Trade with robot">
        {/* We are importing the font this way to lighten the size of SE2. */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link href="https://fonts.googleapis.com/css2?family=Bai+Jamjuree&display=swap" rel="stylesheet" />
      </MetaHeader>
    </>
  );
};

export default Agent;
