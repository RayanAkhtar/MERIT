import { redirect } from 'next/navigation';

export default function ConfigRedirect() {
  redirect('/config/create');
}
